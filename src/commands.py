from time import time

def run(**kwargs):
    import paramiko

    config = kwargs["config"]["ssh"]
    experiment = kwargs["experiment"]

    save_trace = None if "save_trace" not in kwargs else kwargs["save_trace"]
    save_timing = None if "save_timing" not in kwargs else kwargs["save_timing"]

    # Initialise SEcube

    start_time = time()
    with paramiko.SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect(
            config["host"],
            config["port"],
            config["username"],
            config["password"]
        )

        for _ in range(experiment["exec_count"]):
            ssh.exec_command(experiment["command"])
    end_time = time()

    if save_timing:
        save_timing([start_time, end_time, end_time - start_time])
