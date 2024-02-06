ARG PYTORCH_RELEASE="23.08"
ARG PYTHON_VERSION="3"

FROM "nvcr.io/nvidia/pytorch:${PYTORCH_RELEASE}-py${PYTHON_VERSION}"

EXPOSE 80/tcp
WORKDIR /usr/local/bin

RUN pip install --no-cache-dir transformers \
    langchain \
    pymysql

RUN apt-get update && apt-get install -y \
    git \
    mysql-server \
    && rm -rf /var/lib/apt/lists/*

# Configure MySQL (Later use)
# RUN service mysql start && \
#    mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION; FLUSH PRIVILEGES;" && \
#    mysql -e "CREATE DATABASE IF NOT EXISTS ColorPalette;" \
#    mysql -e "CREATE DATABASE IF NOT EXISTS Coop;" \
#    mysql -e "CREATE DATABASE IF NOT EXISTS LLMold;"

CMD [ "/bin/sh" ]


