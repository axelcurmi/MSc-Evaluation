from time import time

def run(**kwargs):
    import docker

    config = kwargs["config"]["ssh"]
    experiment = kwargs["experiment"]

    save_timing = None if "save_timing" not in kwargs \
        else kwargs["save_timing"]

    client = docker.DockerClient(
        base_url="ssh://{}@{}:{}".format(
            config["username"],
            config["host"],
            config["port"]
        )
    )

    try:
        client.images.get(experiment["image"])
    except docker.errors.ImageNotFound:
        client.images.pull(experiment["image"])

    container = client.containers.create(
        experiment["image"],
        experiment["command"])

    start_time = time()
    for _ in range(experiment["exec_count"]):
        container.start()
    end_time = time()

    # Remove all stopped containers
    client.containers.prune()

    # Closes the SSH Client which will also destroy the PySEcube wrapper
    client.api._custom_adapter.ssh_client.close()

    if save_timing:
        save_timing([start_time, end_time, end_time - start_time])