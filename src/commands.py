from time import time, sleep

from pysecube import Wrapper

def run(**kwargs):
    import paramiko

    config = kwargs["config"]["ssh"]
    experiment = kwargs["experiment"]
    with_secube = "with_secube" in kwargs and kwargs["with_secube"]

    pysecube = None
    if with_secube:
        pysecube = Wrapper(b"test")
        pysecube.crypto_set_time_now()

    save_timing = None if "save_timing" not in kwargs \
        else kwargs["save_timing"]

    start_time = time()
    ssh = paramiko.SSHClient()
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

    for _ in range(experiment["exec_count"]):
        ssh.exec_command(experiment["command"])
    ssh.close()
    end_time = time()

    if with_secube:
        sleep(0.5)
        pysecube.destroy()

    if save_timing:
        save_timing([start_time, end_time, end_time - start_time])
