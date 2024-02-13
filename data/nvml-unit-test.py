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
free_gpu_mem = None
occupied_mem_per_proc = {}
device_count = pynvml.nvmlDeviceGetCount()
for i in range(device_count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    free_gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(handle).free # Byte
    try:
        procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        for proc in procs:
            occupied_mem_per_proc[proc.pid] = proc.usedGpuMemory
    except pynvml.NVMLError as e:
        print(f"  Error retrieving processes: {e}")

# (3) Compare (1) and (2)
print(free_gpu_mem)
print(occupied_mem_per_proc)
