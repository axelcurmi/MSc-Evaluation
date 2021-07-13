import docker

client = docker.DockerClient(
    base_url="ssh://user@192.168.1.164:22"
)

container = client.containers.create("alpine", "echo hello world!")
container.start()
print(container.logs())

client.containers.prune()
