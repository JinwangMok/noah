import os
import time
import json
import docker
import requests

WORK_DIR = os.getenv('NOAH_WORK_DIR')
LANG_SERVER_PORT = os.getenv('LANG_SERVER_PORT')
NOAH_PROXY_PORT = os.getenv('NOAH_PROXY_PORT')
SERVER_NAME = os.getenv('SERVER_NAME')
NETWORK_NAME = os.getenv('NETWORK_NAME')
MNT_VOLUME = WORK_DIR+"/models" # Has to be changed with pathlib or something.
URL = f'http://{SERVER_NAME}:{LANG_SERVER_PORT}'

# 추후 없앨 수도 있는 변수들
# --host 0.0.0.0 has to be change in the future for preventing security issues.
CPU_RATE = 512
N_GPU_LAYERS = 99
IPC_MODE = "host"

# MODEL PATH의 경우, model_size.yaml로 알맞은 크기에 해당하는 모델의 PATH를 읽어오는 작업이 필요함.
# MODEL_PATH = "models/7B/llama-2-7b-chat.Q4_K_M.gguf"

docker_client = docker.from_env()

lang_server_container = docker_client.containers.run(
    "ghcr.io/ggerganov/llama.cpp:server-cuda",
    command=f"-m {MODEL_PATH} -c {CPU_RATE} --host 0.0.0.0 --port {LANG_SERVER_PORT} --n-gpu-layers {N_GPU_LAYERS}",
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
    network=NETWORK_NAME
)

time.sleep(10) # 이 부분 /health == ok 확인 받는 걸로 변경

print(f"container ID: {lang_server_container.id} has been successfully created.")

print("Now let's use this LLM server.")

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

