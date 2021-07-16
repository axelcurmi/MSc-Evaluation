import time
from os import path

import paramiko
from paramiko.config import SSH_PORT

from pysecube.wrapper import Wrapper

PYSECUBE_PIN = b"test"

# Variables
HOST = "192.168.1.90"
USERNAME = "user"
PASSWORD = "password"
N = 1

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
        ],
        "macs": [
            "hmac-sha2-512",
            "hmac-sha2-256-etm@openssh.com",
            "hmac-sha2-512-etm@openssh.com",
            "hmac-sha1",
            "hmac-md5",
            "hmac-sha1-96",
            "hmac-md5-96",
        ]
    },
    pysecube=pysecube
)
print("Connected successfully")

sftp = client.open_sftp()

for i in range(N):
    sftp.put(path.join("resources", "1MB.txt"), f"{i}_1MB.txt")
print("file(s) sent successfully")

sftp.close()
client.close()

pysecube.destroy()
