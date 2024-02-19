import json
import requests

URL = 'http://localhost:6060'
headers = {"Content-Type": "application/json"}
data = {"prompt": "Building a website can be done in 10 simple steps:", "stream": True}
stream_response = requests.post(URL+'/completion', headers=headers, data=json.dumps(data), stream=True)
for line in stream_response.iter_lines():
    if line:
        # Looks like: {'content': 'ours', 'multimodal': False, 'slot_id': 0, 'stop': False}
        print(json.loads(line.decode('utf-8'))['content'], end='', flush=True)
else:   
    print()

