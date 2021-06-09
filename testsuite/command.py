import time

import paramiko
from paramiko.config import SSH_PORT

from pysecube.wrapper import Wrapper

PYSECUBE_PIN = b"test"

# Variables
HOST = "172.26.247.148"
USERNAME = "user"
PASSWORD = "password"
COMMAND = "uname -a"

pysecube = Wrapper(PYSECUBE_PIN)
pysecube.crypto_set_time_now()
    
client = paramiko.SSHClient()
client.load_system_host_keys()

print(f"Connecting with {HOST}:{SSH_PORT}")
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
    },
    pysecube=pysecube
)
print("Connected successfully")

channel = client.get_transport().open_channel("session")
channel.exec_command(COMMAND)
stdout = channel.makefile("r", -1)

# Wait for an EOF to be received
while not channel.eof_received:
    time.sleep(0.01)

channel.close()
print(stdout.read().decode())
stdout.close()

client.close()

pysecube.destroy()
