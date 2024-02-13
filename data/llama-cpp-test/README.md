# Llama.cpp Test

Welcome!

This is a repository for test Llama.cpp and langchain.

Before get started, make you sure to build `Dockerfile.llamacpp.devel` image and run docker container using below code.

```bash
docker run -d -it --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -v ~/sandbox/noah/data:/app/noah/data -p 6060:6060 -p 6080:80 -p 6443:443 --name llama-cpp {Image ID}
```

I'm now testing ollama & langchian in below files.
> 1. TBD

---

[Additional Dependencies]

---

[Refrences]
