from paramiko import (SSHClient)
from paramiko.config import SSH_PORT

from pysecube.wrapper import Wrapper

import argparse
import time

parser = argparse.ArgumentParser(
    description="PySEcube test driver")
parser.add_argument("--host", "-H", type=str, required=True)
parser.add_argument("--username", "-u", type=str, required=True)
parser.add_argument("--password", "-p", type=str, required=True)
parser.add_argument("--command", "-c", type=str, required=True)
parser.add_argument("--reps", "-r", type=int, required=True)
args = parser.parse_args()

for i in range(args.reps):
    start_time = None
    end_time = None
    
    try:
        start_time = time.time()

        client = SSHClient()
        client.load_system_host_keys()

        client.connect(args.host, SSH_PORT, args.username, args.password,
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

        client.exec_command(args.command)
        end_time = time.time()

        client.close()
        pysecube.destroy()
    except Exception as e:
        pass

    print(f"{start_time},{end_time},{end_time - start_time}")
