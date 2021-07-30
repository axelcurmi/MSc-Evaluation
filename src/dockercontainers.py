from time import time, sleep

def run(**kwargs):
    import docker

    config = kwargs["config"]["ssh"]
    experiment = kwargs["experiment"]
    with_secube = "with_secube" in kwargs and kwargs["with_secube"]

    save_timing = None if "save_timing" not in kwargs \
        else kwargs["save_timing"]
    add_secube_metrics = None if "add_secube_metrics" not in kwargs \
        else kwargs["add_secube_metrics"]

    client = docker.DockerClient(
        base_url="ssh://{}@{}:{}".format(
            config["username"],
            config["host"],
            config["port"]
        )
    )

    container = client.containers.create(experiment["image"])

    container.start()

    start_time = time()
    for _ in range(experiment["exec_count"]):
        container.logs()
    end_time = time()

    if with_secube and add_secube_metrics:
        add_secube_metrics(client.api._custom_adapter\
            .ssh_client.get_transport().pysecube.get_metrics())

    if with_secube:
        sleep(0.5)

    # Remove all stopped containers
    client.containers.prune()

    # Closes the SSH Client which will also destroy the PySEcube wrapper
    client.api._custom_adapter.ssh_client.close()

    if save_timing:
        save_timing([start_time, end_time, end_time - start_time])