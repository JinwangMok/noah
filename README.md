# ⛴️  Noah

Noah is a all-in-one project for handling local/cloud ensembled Langchain chatbot application reveraging Streamlit.

## Description

Noah is constructed three (or two) local container.
- `noah_app`: A Streamlit application containing customLLM class of Langchain called 'NoahLLM' which port number is 8501. 
- `noah`: A proxy server with 6060 port which automatically control what model should be ran on local GPU or (if any models can't be used) cloud backend. 
- `lang_server`: A local Llama.cpp language server container which port number is 6061. It automatically stopped/started by `noah` proxy server and flexibly be changed its language model by pre-downloaded LLM(gguf/ggml) in `model` directory.


Noah can...
- makes your actual cost reduce by leveraging local GPU with cloud backend resources (or ChatGPT API). Especially, it uses pynvml which is python wrapper for NVML for NVIDIA GPU.
- makes you free to concern about GPU memory. If your local GPU memory is full by different process, it will magically stop your local language server and you can get your GPU memory back.
- gives you a simple demo for local Langchain application with Streamlit. It will help you to build your own chatbot system. 


Note: Noah support NVIDIA GPU only.

---

## Usage
1. download this repository and install docker. (ref: docker_install.sh)
2. move to root directory of this project.
3. type `./app.sh` and enter!
4. Enjoy your demo application at `http://localhost:8501`.
