import docker

docker_client = docker.from_env()

try:
    lang_server_container = docker_client.containers.get("lang_server")
    lang_server_container.stop()
    lang_server_container.remove()
    print("Successfully stop and remove lang_server.")
except docker.errors.NotFound:
    print("Can not found container named 'lang_server'.")
except Exception as e:
    print(f"Error occured: {e}")
