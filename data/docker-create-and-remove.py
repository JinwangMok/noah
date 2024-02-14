import docker
import requests
import json
import time

WORK_DIR = "/home/jinwang/sandbox/noah"
MODEL_PATH = "models/7B/llama-2-7b-chat.Q4_K_M.gguf"
CPU_RATE = 512
PORT = 8080
N_GPU_LAYERS = 99
# --host 0.0.0.0 has to be change in the future for preventing security issues.
SERVER_NAME = "lang_server"
IPC_MODE = "host"
MNT_VOLUME = WORK_DIR+"/models" # Has to be changed with pathlib or something.
NETWORK_NAME = "lang_pipe"

docker_client = docker.from_env()

lang_server_container = docker_client.containers.run(
    "ghcr.io/ggerganov/llama.cpp:server-cuda",
    command=f"-m {MODEL_PATH} -c {CPU_RATE} --host 0.0.0.0 --port {PORT} --n-gpu-layers {N_GPU_LAYERS}",
    name=SERVER_NAME,
    detach=True,
    device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],
    ipc_mode=IPC_MODE,
    ulimits=[
        docker.types.Ulimit(name='memlock', soft=-1, hard=-1),
        docker.types.Ulimit(name='stack', soft=67108864, hard=67108864)
    ],
    volumes={
       WORK_DIR+"/models": {'bind': '/models'}
    },
    ports={f'{PORT}/tcp':PORT},
    network=NETWORK_NAME
)

time.sleep(10)
print(f"container ID: {lang_server_container.id} has been successfully created.")

print("Now let's use this LLM server.")
URL = 'http://lang_server:8080'

health_response = requests.request('GET', URL+'/health')
print(health_response)

print("-"*50)

headers = {"Content-Type": "application/json"}
data = {"prompt": "Building a website can be done in 10 simple steps:", "stream": True}

stream_response = requests.post(URL+'/completion', headers=headers, data=json.dumps(data), stream=True)

for line in stream_response.iter_lines():
    if line:
        print(line.decode('utf-8'))

print("MISSION COMPLETE. NOW SERVER WILL BE TERMINATED.")

lang_server_container.stop()
lang_server_container.remove()

print("And now it successfully removed.")
