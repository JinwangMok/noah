# app/Dockerfile

FROM python:3.9-slim

ARG NOAH_WORK_DIR
ARG NOAH_PROXY_PORT

ENV NOAH_WORK_DIR=${NOAH_WORK_DIR}
ENV NOAH_PROXY_PORT=${NOAH_PROXY_PORT}

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install streamlit langchain

RUN mkdir ./server
COPY ./server /app/server

EXPOSE 8501

WORKDIR /app/server
CMD ["streamlit", "run", "app.py"]
# ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
# RUN rm -rf streamlit_app.py
# NEW file is needed.

