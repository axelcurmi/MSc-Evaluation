from time import time

def run(**kwargs):
    import paramiko

    config = kwargs["config"]["ssh"]
    experiment = kwargs["experiment"]

    assert len(experiment["sessions"]) == len(experiment["exec_count"]), \
        "'sessions' and 'exec_count' should be equal in size"

    for j in range(len(experiment["sessions"])):
        for session_id in range(experiment["sessions"][j]):
            
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

                for _ in range(experiment["exec_count"][j]):
                    ssh.exec_command(experiment["command"])
            end_time = time()

            # Save trace in a file
            if kwargs["save_trace_callback"]:
                kwargs["save_trace_callback"](session_id)
            kwargs["save_timing"]([start_time, end_time, end_time - start_time])
