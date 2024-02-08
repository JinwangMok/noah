# Ollama Test

Welcome!

This is a repository for test Ollama and langchain.

Before get started, make you sure to build `Dockerfile.ollama.devel` image and run docker container using below code.

```bash
docker run -d -it --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -v ~/sandbox/noah/data:/app/noah/data -p 11434:11434 -p 9080:80 -p 9443:443 --name ollama_test {Image ID}
```

And then run ollama server via `ollama serve`.

If you want to test in basic llama2 model then also excute `ollama pull llama2`. 

That's it!

I'm now testing ollama & langchian in below files.
> 1. `ollama-simple-stream.py`: Just simple usage.
> 
> 2. 

---

[Additional Dependencies]
- beautifulsoup4, faiss-cpu,  

---

[Refrences]
> 1. [LangChain Quickstart](https://python.langchain.com/docs/get_started/quickstart")
