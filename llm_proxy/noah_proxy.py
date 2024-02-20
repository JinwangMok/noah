import os
import sys
import signal
import atexit
import time
import yaml
import json
import pynvml
import docker
import requests
from flask import Flask, request, jsonify, Response
import threading

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

NOAH_PROXY_PORT = os.getenv('NOAH_PROXY_PORT')

class Noah():
    def __init__(self):
        # Single GPU support untill now. (device:0)
        self.is_nvml_available = True
        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except pynvml.NVMLError as e:
            logger.debug(e)
            self.is_nvml_available = False
            # valid check: Noah().is_nvml_available() 
            return

        with open('./model_size.yaml', 'r') as fp:
            self.model_specs = yaml.safe_load(fp)['models']
        self.gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
        self.selected_model_spec = self.__get_largest_llm_spec()
        self.gpu_mem_threshold = self.__calc_gpu_mem_threshold()             
        self.last_gpu_mem_used = self.gpu_mem.used
        self.is_local_llm_running = False

        self.__docker_client = docker.from_env()
        self.__local_llm_container = None
        self.__WORK_DIR = os.getenv('NOAH_WORK_DIR')
        self.__LANG_SERVER_NAME = os.getenv('LANG_SERVER_NAME')
        self.__LANG_SERVER_PORT = os.getenv('LANG_SERVER_PORT')
        self.__EXTERNAL_SERVER_NAME = os.getenv('EXTERNAL_SERVER_NAME')
        self.__EXTERNAL_SERVER_PORT = os.getenv('EXTERNAL_SERVER_PORT')
        self.__NETWORK_NAME = os.getenv('NETWORK_NAME')
        self.__LOCAL_URL = f'http://{self.__LANG_SERVER_NAME}:{self.__LANG_SERVER_PORT}'
        self.__EXTERNAL_URL = f'http://{self.__EXTERNAL_SERVER_NAME}:{self.__EXTERNAL_SERVER_PORT}'

    def __get_largest_llm_spec(self):
        max_model_spec = {'path':None, 'size':0}
        for model_spec in self.model_specs:
            if (model_spec['size'] < self.gpu_mem.free) and (model_spec['size'] > max_model_spec['size']):
                max_model_spec = model_spec
        return max_model_spec

    def __calc_gpu_mem_threshold(self):
        return int((self.gpu_mem.total - (self.gpu_mem.used + self.selected_model_spec['size']))/2)

    def run(self):
        while True:
            logger.debug("Polling NVIDIA GPU...")
            logger.debug(self.gpu_mem_threshold)
            logger.debug(self.gpu_mem.free)
            self.gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            if self.is_local_llm_running:
                if self.gpu_mem.free < self.gpu_mem_threshold:
                    # Lack of GPU memory.
                    self.is_local_llm_running = False
                    self.__stop_local_llm()
                if self.last_gpu_mem_used != self.gpu_mem.used:
                    # GPU memory has been changed.
                    if self.__check_larger_llm_exists():
                        self.is_local_llm_running = False
                        self.__stop_local_llm()
            else:
                self.selected_model_spec = self.__get_largest_llm_spec()
                if self.selected_model_spec['size'] > 0:
                    self.is_local_llm_running = self.__start_local_llm()
            self.last_gpu_mem_used = self.gpu_mem.used
            time.sleep(0.5)

    def __check_larger_llm_exists(self):
        for model_spec in self.model_specs:
            if model_spec['size'] < (self.gpu_mem.free + self.selected_model_spec['size']) and (self.selected_model_spec['path'] != model_spec['path']):
                return True
        return False

    def __poll_gpu_stat(self):
        self.gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
        if self.is_local_llm_running:
            if self.gpu_mem.free < self.gpu_mem_threshold:
                return False
            return True
        elif self.__gpu_proc_cnt != (gpu_procs := len(pynvml.nvmlDeviceGetComputeRunningProcesses(self.gpu_handle))):
            self.__gpu_proc_cnt = gpu_procs
            self.selected_model_spec = self.__get_largest_llm_spec()

    def __start_local_llm(self):
        self.__local_llm_container = self.__docker_client.containers.run(
                "ghcr.io/ggerganov/llama.cpp:server-cuda",
                command=f"-m {self.selected_model_spec['path'][2:]} --host 0.0.0.0 --port {self.__LANG_SERVER_PORT}",
                name=self.__LANG_SERVER_NAME,
                detach=True,
                device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],
                ipc_mode="host",
                ulimits=[
                    docker.types.Ulimit(name='memlock', soft=-1, hard=-1),
                    docker.types.Ulimit(name='stack', soft=67108864, hard=67108864)
                ],
                volumes={self.__WORK_DIR+"/models":{"bind":"/models"}},
                network=self.__NETWORK_NAME
        )
        time.sleep(3)
        tolerance = 10
        while not self.__local_llm_health_check():
            if tolerance <= 0:
                return False
            tolerance -= 1
            logger.debug("Trying to health check of local LLM server...")
            time.sleep(1)
        self.gpu_mem_threshold = self.__calc_gpu_mem_threshold()             
        logger.debug("Local LLM server is now running!")
        return True
    
    def __stop_local_llm(self):
        try:
            self.__local_llm_container.stop()
            self.__local_llm_container.remove()
        except pynvml.NVMLError as e:
            logger.debug(e)
            return False
        return True

    def __local_llm_health_check(self):
        if requests.get(self.__LOCAL_URL+'/health').json()['status'] == "ok":
            return True
        return False

    def get_url(self):
        if self.is_local_llm_running:
            logger.debug(f"Request to {self.__LOCAL_URL}")
            return self.__LOCAL_URL
        else:
            logger.debug(f"Request to {self.__EXTERNAL_URL}")
            return self.__EXTERNAL_URL
    def clean_up(self):
        try:
            self.__local_llm_container.stop()
            self.__local_llm_container.remove()
        except pynvml.NVMLError as e:
            logger.debug(e)


class ResilientThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs if kwargs is not None else {}
        self.running = True

    def run(self):
        while self.running:
            try:
                self.target(*self.args, **self.kwargs)
            except Exception as e:
                logger.debug("Error occured in noah.run thread. Try to restart...")
                time.sleep(1)

    def stop(self):
        self.running = False


app = Flask(__name__)
noah = Noah()

@app.route('/health', methods=['GET'])
def health_check():
    data = request.args
    url = noah.get_url()
    response = requests.get(url+'/health').json() 
    return response

@app.route('/completion', methods=['POST'])
def handle_completion():
    data = request.json #dict
    if not data:
        return jsonify(error='No data provided'), 400
    url = noah.get_url()
    response = requests.post(url+'/completion', headers={'Content-Type':'application/json'}, data=json.dumps(data), stream=True)
    def generate():
        for chunk in response.iter_lines():
            if chunk:
                yield f"{chunk.decode('utf-8').split('data: ')[1]}\n".encode('utf-8') # class: bytes
    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    def clean_up():
        logger.debug("clean_up called!")
        global noah
        noah.clean_up()
    def cleaned_up_by_sig(signum, frame):
        logger.debug("clean_up_by_sig called!")
        global noah
        noah.clean_up()
        sys.exit(0)
    atexit.register(clean_up)
    signal.signal(signal.SIGINT, cleaned_up_by_sig)
    signal.signal(signal.SIGTERM, cleaned_up_by_sig)

    thread = ResilientThread(target=noah.run)
    thread.start()

    app.run(host='0.0.0.0', port=NOAH_PROXY_PORT, debug=True, use_reloader=False)
