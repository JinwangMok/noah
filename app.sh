#!/bin/bash

# 도커 설치 되었다고 가정. 설치 파일은 docker_install.sh 참고.

# noah 관련 환경 변수 설정
export NOAH_WORK_DIR=$(pwd)
export LANG_SERVER_PORT=6061
export NOAH_PROXY_PORT=6060
export LANG_SERVER_NAME=lang_server
export NETWORK_NAME=lang_pipe

# 기타 환경 변수 설정
export WEB_SERVER_PORT=8080

# ./models 안에 모델 다운로드 (향후 모델 다양하게 추가해야 함)


# model_size.yaml 생성 필요
chmod +x update_model_size.sh
./update_model_size.sh

# Dockerfile로부터 이미지 생성 (Llama.cpp 서버 / noah)
docker pull ghcr.io/ggerganov/llama.cpp:server-cuda
docker build -f Dockerfile.noah \
             --build-arg NOAH_WORK_DIR=$NOAH_WORK_DIR \
             --build-arg LANG_SERVER_PORT=$LANG_SERVER_PORT \
             --build-arg NOAH_PROXY_PORT=$NOAH_PROXY_PORT \
             --build-arg LANG_SERVER_NAME=$LANG_SERVER_NAME \
             --build-arg NETWORK_NAME=$NETWORK_NAME \
             -t noah:dev .

# 네트워크
if ! docker network ls | grep -q $NETWORK_NAME; then
	docker network create lang_pipe
else
	echo "Network $NETWORK_NAME already exists."
fi

# noah (proxy) 컨테이너 실행 (DooD) (-it 제거함)
docker run -d --gpus all -v /var/run/docker.sock:/var/run/docker.sock -p 6060:6060 --network lang_pipe --name noah noah:dev

# 스트림릿 웹 서버 컨테이너 실행

# URL 출력

# Done!
