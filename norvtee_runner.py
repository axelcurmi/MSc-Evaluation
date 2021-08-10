import csv
import time

from datetime import datetime
from os import (path, mkdir)

import paramiko
from paramiko.config import SSH_PORT

# Variables
# HOST = "192.168.37.136"
HOST = "192.168.1.50"
USERNAME = "user"
PASSWORD = "password"
COMMAND = "uname -a"
SAVE_TRACE = False
N = 1
CMD_PER_N = 1000

TEST_TIME = datetime.now().strftime("%Y%m%d%H%M%S")
OUT_DIR = path.join("out", "norvtee", TEST_TIME)

timings = []

def save_timings():
    global timings

    # If the target directory does not exist, create it
    if not path.exists(OUT_DIR):
        mkdir(OUT_DIR)
    
    with open(path.join(OUT_DIR, "timings.csv"), "w", newline="") as stream:
        csv_out=csv.writer(stream)
        csv_out.writerow(["start_time", "end_time", "time_taken"])
        for timing in timings:
            csv_out.writerow(timing)

print(f"Result(s) will be saved in {OUT_DIR}")

for i in range(N):
    start_time = None
    end_time = None

    try:
        start_time = time.time()

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
            }
        )
        print("Connected successfully")

        for j in range(CMD_PER_N):
            channel = client.get_transport().open_channel("session")
            channel.exec_command(COMMAND)
            stdout = channel.makefile("r", -1)

            # Wait for an EOF to be received
            while not channel.eof_received:
                time.sleep(0.01)

            channel.close()
            print(f"[{i}:{j}] {stdout.read().decode()}")
            stdout.close()

        client.close()
        end_time = time.time()
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
        pass

    if start_time is not None and end_time is not None:
        timings.append((start_time, end_time, end_time - start_time))

if len(timings) > 0:
    save_timings()
