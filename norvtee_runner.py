from paramiko import (SSHClient)
from paramiko.config import SSH_PORT

from pysecube.wrapper import Wrapper

import time

# Variables
# HOST = "192.168.37.136"
HOST = "172.20.9.119"
USERNAME = "user"
PASSWORD = "password"
COMMAND = "uname -a"
SAVE_TRACE = True
N = 1

for i in range(N):
    start_time = None
    end_time = None
    
    try:
        start_time = time.time()

        client = SSHClient()
        client.load_system_host_keys()

        client.connect(HOST, SSH_PORT, USERNAME, PASSWORD,
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
            }
        )

        client.exec_command(COMMAND)
        end_time = time.time()

        client.close()
    except Exception as e:
        pass

    print(f"{start_time},{end_time},{end_time - start_time}")
