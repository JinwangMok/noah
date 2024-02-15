import os
from flask import Flask

NOAH_PROXY_PORT = os.getenv('NOAH_PROXY_PORT')

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=NOAH_PROXY_PORT)
