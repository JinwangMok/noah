import pynvml
import yaml

# Checking GPU type is NVIDIA will be added in the future.
# (maybe in the very first step of this project like .sh)

pynvml.nvmlInit()

# 1. A local LLM server is running?
# Later with `docker` lib.

# 1-y. LLM requests - done.
# 1-n. continue

# 2. GPU is available?
# (1) Get LLMs' size. (ref: updateModelSizeFile.sh)
model_size_fp = "/app/noah/data/model_sizes.yaml"
with open(model_size_fp, "r") as file:
    model_size_list = yaml.safe_load(file)['models']

# (2) Get current GPU available memory.
available_gpu_mem = 0
occupied_mem_per_proc = {}
device_count = pynvml.nvmlDeviceGetCount()
for i in range(device_count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    available_gpu_mem += pynvml.nvmlDeviceGetMemoryInfo(handle).free # Byte
    try:
        procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        for proc in procs:
            occupied_mem_per_proc[proc.pid] = proc.usedGpuMemory
    except pynvml.NVMLError as e:
        print(f"  Error retrieving processes: {e}")

# (3) Compare (1) and (2)
model_candidates = []
for model_data in model_size_list:
    if model_data["size"] < available_gpu_mem:
        print(f"We can use {model_data['name']}.")
        model_candidates.append(model_data)

# (4) Select LLM backend.
selected_model = None
if len(model_candidates) < 1:
    print("We have to use MobileX backend. Local GPU is unavailable now.")
else:
    selected_model_size = 0
    for model_data in model_candidates:
        if model_data["size"] > selected_model_size:
            selected_model = model_data["name"]
            selected_model_size = model_data["size"]

# (5) Final Decision
if selected_model:
    print(selected_model)
else:
    print("MobileX Backend")
