# **NOAH**

A **N**imble, **O**ptimal, **A**utomatic and **H**andy LLM Manager.

## Development Instructions (Personal Usage)

```
This README file is JUST a note now. It will be updated to proper style later.
```

0. Move your current directory to proper workspace.

1. Docker start
> `sudo systemctl start docker`

2. (Once) Build docker image
> `docker build -f Dockerfile.devel -t noah-test-image:devel .`

3. Check the image ID
> `docker images`

3. Mount and port forwarding
> `docker run -d -it --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -v ~/{PATH}/data:/app/noah/data -p 6060:6060 --name noah_test {Image ID}`

4. Access to container
> `docker exec -it noah_test /bin/bash`
