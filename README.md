# **NOAH**: **N**imble, **O**ptimal, **A**utomatic and **H**andy LLM Manager

## (Personal Usage) Development Setting

1. Docker start
> `sudo systemctl docker start`

2. (optional) Build docker image
> `docker build -f Dockerfile.devel -t noah-test:devel`

3. Mount and port forwarding
> `docker run -v $(pwd)/{my path here}:/{mount dir here} -p {container port}:{host port} --name noah-test-cont noah-test`

4. Access to container
> `docker exec -it noah-test-cont /bin/bash
