import argparse
import csv
import json
import time

from datetime import datetime
from os import path, mkdir

import aspectlib
import paramiko

from paramiko.config import SSH_PORT

from pysecube.wrapper import Wrapper

PYSECUBE_PIN = b"test"
TEST_TIME = datetime.now().strftime("%Y%m%d%H%M%S")
OUT_DIR = path.join("out", "rvtee", TEST_TIME)

trace = []
timings = []

def save_and_clear_trace(trace_id):
    global trace

    # If the target directory does not exist, create it
    if not path.exists(OUT_DIR):
        mkdir(OUT_DIR)

    with open(path.join(OUT_DIR, f"{trace_id}.json"), "w") as stream:
        json.dump(trace, stream, indent=4)

    # Clear
    trace = []

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

def add_event(when, what, scope, watch, func_args, func_kwargs):
    global trace

    trace.append(
        {
            "timestamp": int(time.time()),
            "when": when,
            "what": what,
            "scope": scope,
            "watch": watch,
            "func_args": func_args,
            "func_kwargs": func_kwargs,
        }
    )

# The "none" cipher is provided for debugging and SHOULD NOT be used
# except for that purpose.
@aspectlib.Aspect
def paramiko_transport_send_kex_init(*args, **kwargs):
    add_event("BEFORE", "_send_kex_init", "paramiko.Transport", {
        "preferred_ciphers": args[0].preferred_ciphers
    }, args[1:], kwargs)
    try:
        yield
    except Exception as e:
        raise
    finally:
        pass
aspectlib.weave(paramiko.Transport._send_kex_init,
                paramiko_transport_send_kex_init)

# CLI argument parsing
parser = argparse.ArgumentParser(
    description="PySEcube test driver")
parser.add_argument("--host", "-H", type=str, required=True)
parser.add_argument("--username", "-u", type=str, required=True)
parser.add_argument("--password", "-p", type=str, required=True)
parser.add_argument("--command", "-c", type=str, required=True)
parser.add_argument("--reps", "-r", type=int, required=True)
args = parser.parse_args()

print(f"Result(s) will be saved in {OUT_DIR}")

for i in range(args.reps):
    start_time = None
    end_time = None

    pysecube = Wrapper(PYSECUBE_PIN)
    pysecube.crypto_set_time_now()
    
    try:
        start_time = time.time()

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

        client.exec_command(args.command)
        end_time = time.time()

        client.close()
        pysecube.destroy()
    except Exception as e:
        print(e)
        pass

    timings.append((start_time, end_time, end_time - start_time))

    save_and_clear_trace(i)
save_timings()
