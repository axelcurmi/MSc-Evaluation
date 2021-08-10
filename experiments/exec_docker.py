import docker
import time

for i in range(2):
    print(" >> {}".format(i))
    client = docker.DockerClient(
        base_url="ssh://user@192.168.1.90:22"
    )

    try:
        client.images.get("alpine")
    except docker.errors.ImageNotFound:
        client.images.pull("alpine")

    t0 = time.time()
    container = client.containers.create("alpine", "echo hello world!")
    t1 = time.time()
    print("t1: ", t1 - t0)

    for _ in range(1):
        container.start()
    t2 = time.time()
    print("t2: ", t2 - t0)

    print(container.logs())
    t3 = time.time()
    print("t3: ", t3 - t2)

    client.containers.prune()

    client.api._custom_adapter.ssh_client.close()
