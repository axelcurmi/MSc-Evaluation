from time import (time, sleep)

def run(**kwargs):
    import paramiko

    config = kwargs["config"]["ssh"]
    experiment = kwargs["experiment"]
    pysecube = kwargs["pysecube"]

    save_timing = None if "save_timing" not in kwargs \
        else kwargs["save_timing"]

    start_time = time()
    with paramiko.SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect(
            config["host"],
            config["port"],
            config["username"],
            config["password"],
            disabled_algorithms={
                # Force KEX engine to use DH Group 14 with SHA256
                "kex": [
                    "curve25519-sha256@libssh.org",
                    "ecdh-sha2-nistp256",
                    "ecdh-sha2-nistp384",
                    "ecdh-sha2-nistp521",
                    "diffie-hellman-group16-sha512",
                    "diffie-hellman-group-exchange-sha256",
                    "diffie-hellman-group-exchange-sha1",
                    "diffie-hellman-group14-sha1",
                    "diffie-hellman-group1-sha1",
                ]
            },
            pysecube=pysecube
        )

        shell = ssh.invoke_shell()
        for i in range(experiment["exec_count"]):
            while not shell.send_ready():
                sleep(0.05)

            shell.send("uname -a\n")

            while not shell.recv_ready():
                sleep(0.05)

            shell.recv(4096)
        shell.close()
    end_time = time()

    if save_timing:
        save_timing([start_time, end_time, end_time - start_time])
