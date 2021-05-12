import argparse
import paramiko

from paramiko.config import SSH_PORT
from pysecube.wrapper import Wrapper

PYSECUBE_PIN = b"test"

# CLI argument parsing
parser = argparse.ArgumentParser(
    description="PySEcube test driver")
parser.add_argument("--host", "-H", type=str, required=True)
parser.add_argument("--username", "-u", type=str, required=True)
parser.add_argument("--password", "-p", type=str, required=True)
parser.add_argument("--command", "-c", type=str, required=True)
args = parser.parse_args()

pysecube = Wrapper(PYSECUBE_PIN)
pysecube.crypto_set_time_now()

try:
    client = paramiko.SSHClient()
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
        },
        pysecube=pysecube
    )

    _, stdout, _ = client.exec_command(args.command)
    print(stdout.read().decode())

    client.close()
    pysecube.destroy()
except Exception as e:
    print(f"{type(e).__name__}: {e}")
    pass
