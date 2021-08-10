import paramiko
from paramiko.config import SSH_PORT

# import logging
# logging.basicConfig()
# logging.getLogger("paramiko").setLevel(logging.DEBUG)

# Variables
HOST = "192.168.1.90"
USERNAME = "user"
PASSWORD = "password"
COMMAND = "uname -a"

client = paramiko.SSHClient()
client.load_system_host_keys()

print(f"Connecting with {HOST}:{SSH_PORT}")
client.connect(HOST, SSH_PORT, USERNAME, PASSWORD)
print("Connected successfully")

_, stdout, _ = client.exec_command(COMMAND)
print(stdout.read().decode())

client.close()
