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

@aspectlib.Aspect
def _send_kex_init_aspect(*args, **kwargs):
    add_event("BEFORE", "_send_kex_init", "paramiko.Transport", {
        "preferred_ciphers": args[0].preferred_ciphers
    }, [], {})
    try:
        yield
    except Exception as e:
        raise
    finally:
        pass
aspectlib.weave(paramiko.Transport._send_kex_init, _send_kex_init_aspect)

@aspectlib.Aspect
def read_message_aspect(*args, **kwargs):
    add_event("BEFORE", "read_message", "paramiko.Packetizer", {
        "mac_engine_set": args[0]._Packetizer__mac_size_in > 0
    }, [], {})
    try:
        yield
    except Exception as e:
        add_event(type(e).__name__, "read_message", "paramiko.Packetizer",
            {}, [], {})
        raise
    finally:
        add_event("AFTER", "read_message", "paramiko.Packetizer", {}, [], {})
aspectlib.weave(paramiko.Packetizer.read_message, read_message_aspect)

@aspectlib.Aspect
def constant_time_bytes_eq_aspect(*args, **kwargs):
    add_event("BEFORE", "constant_time_bytes_eq", "paramiko.util", {}, [], {})
    try:
        yield
    except Exception as e:
        raise
    finally:
        pass
aspectlib.weave(paramiko.util.constant_time_bytes_eq,
                constant_time_bytes_eq_aspect)

@aspectlib.Aspect
def connect_aspect(*args, **kwargs):
    add_event("BEFORE", "connect", "paramiko.SSHClient", {
        "host_in_system_host_keys": \
            args[0]._system_host_keys.get(args[1]) is not None,
        "host_in_host_keys": args[0]._host_keys.get(args[1]) is not None,
    }, [], {})
    try:
        yield
    except Exception as e:
        add_event(type(e).__name__, "connect", "paramiko.SSHClient",
            {}, [], {})
        raise
    finally:
        add_event("AFTER", "connect", "paramiko.SSHClient", {}, [], {})
aspectlib.weave(paramiko.SSHClient.connect, connect_aspect)

@aspectlib.Aspect
def _parse_kexecdh_reply_aspect(*args, **kwargs):
    add_event("BEFORE", "_parse_kexdh_reply", "paramiko.kex_group14.KexGroup14",
              {}, [], {})
    try:
        yield
    except Exception as e:
        raise
    finally:
        add_event("AFTER", "_parse_kexdh_reply",
            "paramiko.kex_group14.KexGroup14", {
                "x_cleared": args[0].x is None or args[0].x == 0
            }, [], {})
aspectlib.weave(paramiko.kex_group14.KexGroup14._parse_kexdh_reply,
                _parse_kexecdh_reply_aspect)

@aspectlib.Aspect
def verify_ssh_sig_aspect(*args, **kwargs):
    add_event("BEFORE", "verify_ssh_sig_aspect", "paramiko.ECDSAKey",
              {}, [], {})
    try:
        yield
    except Exception as e:
        raise
    finally:
        pass
aspectlib.weave(paramiko.ECDSAKey.verify_ssh_sig, verify_ssh_sig_aspect)

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
        # print(f"{type(e).__name__}: {e}")
        pass

    if start_time is not None and end_time is not None:
        timings.append((start_time, end_time, end_time - start_time))

    save_and_clear_trace(i)

if len(timings):
    save_timings()
