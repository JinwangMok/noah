import time
import pynvml

pynvml.nvmlInit()

# ASSUME THAT WE HAVE A PID & T/F FOR LOCAL LLM SERVER ON ENVIRONMENT VARIABLES.
# Wirte a code for this.
# Run local llm container and save env_var & PID here. (TBD)
LOCAL_LLM_IS_RUNNING = True # For test
LOCAL_LLM_PID = 890288      # For test

LAST_PROC_CNT = None
LAST_AVL_GPU_MEM = None

def poll_gpu_status():
    # True: A local LLM server be approved to run.
    # False: A local LLM server be rejected to run.
    global LAST_PROC_CNT
    global LAST_AVL_GPU_MEM

    process_count = 0
    available_gpu_mem = 0
        
    try:
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            available_gpu_mem += pynvml.nvmlDeviceGetMemoryInfo(handle).free
            procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
            process_count += len(procs)
    except pynvml.NVMLError as e:
        print(f"  Error retrieving processes: {e}")
   
    # For test.
    print(process_count, available_gpu_mem)

    if (LAST_PROC_CNT is None) and (LAST_AVL_GPU_MEM is None):
        # Initialization
        LAST_PROC_CNT = process_count
        LAST_AVL_GPU_MEM = available_gpu_mem
        return True

    if (LAST_PROC_CNT == process_count) and (LAST_AVL_GPU_MEM == available_gpu_mem):
        # Nothing Changed
        return True   

    # If any process is added OR (consequently) available GPU memory is shrank,
    # Then Stop local LLM server right away.
    
    # coding here! TBD
    print("Docker stopped local LLM server")
    return False
    #     NOTE: In the future, it can be possible that restart OR reinitialize local LLM server by available GPU memory after this new process is successfully added.


while LOCAL_LLM_IS_RUNNING:
    LOCAL_LLM_IS_RUNNING = poll_gpu_status()
    time.sleep(0.5)


print("nvml-watcher is now stop watching.")
