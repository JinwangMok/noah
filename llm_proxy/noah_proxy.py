import os
import time
import yaml
import json
import pynvml
import docker
import requests
from flask import Flask, request, jsonify, Response

# Algorithm
# [DONE]1. Get current local GPU avaliable status.
# [DONE]2. Get available model size file.
# [DONE]3. Select (run local LLM container) or (wait & using backend LLM container)
# 4. Initial prepared  model proxy health check
# 5. Run LLM proxy server.
# 6. Run local GPU watcher.

# TO DO
# 1. Noah::Local Llama.cpp container control by GPU status (docker, nvml)
# 2. Noah::response type handling for acting with langchain OpenAI class

class Noah():
    def __init__(self):
        # Single GPU support untill now. (device:0)
        self.is_nvml_available = True

        try:
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except pynvml.NVMLError as e:
            print(e)
            self.is_nvml_available = False
            # valid check: Noah().is_nvml_available() 
            return

        with open('./model_size.yaml', 'r') as fp:
            self.model_specs = yaml.safe_load(file)['models']
        self.gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
        self.selected_model_spec = self.__get_largest_llm_spec()
        self.gpu_mem_threshold = self.__calc_gpu_mem_threshold()             
        self.last_gpu_mem_used = self.gpu_mem.used
        self.is_local_llm_running = False

        self.__docker_client = docker.from_env()
        self.__local_llm_container = None
        self.__WORK_DIR = os.getenv('NOAH_WORK_DIR')
        self.__LANG_SERVER_PORT = os.getenv('LANG_SERVER_PORT')
        self.__NOAH_PROXY_PORT = os.getenv('NOAH_PROXY_PORT')
        self.__SERVER_NAME = os.getenv('SERVER_NAME')
        self.__NETWORK_NAME = os.getenv('NETWORK_NAME')
        self.__URL = f'http://{SERVER_NAME}:{LANG_SERVER_PORT}'

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
            self.gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            if self.is_local_llm_running:
                if self.gpu_mem.free < self.gpu_mem_threshold:
                    # Lack of GPU memory.
                    self.is_local_llm_running = self.__stop_local_llm()
                if self.last_gpu_mem_used != self.gpu_mem.used:
                    # GPU memory has been changed.
                    if self.__larger_llm_exists():
                        self.is_local_llm_running = self.__stop_local_llm()
            else:
                self.selected_model_spec = self.__get_largest_llm_spec()
                if self.selected_model_spec['size'] > 0:
                    self.is_local_llm_running = self.__start_local_llm()
            self.last_gpu_mem_used = self.gpu_mem.used
            time.sleep(0.5)

    def __larger_llm_exists(self):
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
        self.__local_llm_container = self.__docker_client.run(
                "ghcr.io/ggerganov/llama.cpp:server-cuda",
                command=f"-m {self.selected_model_spec['path'][2:]} --host 0.0.0.0 --port {self.__LANG_SERVER_PORT}",
                name=self.__SERVER_NAME,
                detach=True,
                device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],
                ipc_mode="host",
                ulimits=[
                    docker.types.Ulimit(name='memlock', soft=-1, hard=-1)
                ],
                volumes={self.__WORK_DIR+"/models":{"bind":"/models"}},
                network=self.__NETWORK_NAME
        )
        tolerance = 10
        while not self.__local_llm_health_check():
            if tolerance <= 0:
                return False
            tolerance -= 1
            print("Trying to health check of local LLM server...")
            time.sleep(1)
        self.gpu_mem_threshold = self.__calc_gpu_mem_threshold()             
        print("Local LLM server is now running!")
        return True
    
    def __stop_local_llm(self):
        try:
            self.__local_llm_container.stop()
            self.__local_llm_container.remove()
        except pynvml.NVMLError as e:
            print(e)
            return False
        return True

    def __local_llm_health_check(self):
        if requests.get(URL+'/health').json()['status'] == "ok":
            return True
        return False

    def __del__(self):
        try:
            self.__local_llm_container.stop()
            self.__local_llm_container.remove()
        except pynvml.NVMLError as e:
            print(e)
    
def hello_world():
    return 'BAD URI'

@app.route('/health', methods=['GET'])
def health_check():
    # GPU / Backend Resource Checking
    return jsonify(status='UP'), 200

@app.route('/completion', methods=['POST'])
def handle_completion():
    # GPU / Backend Resource Logic
    data = request.get_json()

    if not data:
        return jsonify(error='No data provided'), 400

    def generate():
        for word in response.iter_line():
            yield word
    return Response(generate(), content_type=response.headers['Content-Type'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=NOAH_PROXY_PORT)
