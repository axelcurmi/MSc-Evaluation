import ctypes
import sys

import paramiko

x_address = None
x_size = None

x_bytes_before = None

def patch_parse_newkeys(func):
    def inner(*args, **kwargs):
        global x_address, x_size, x_bytes_before

        x_address = id(args[0].kex_engine.x)
        x_size = sys.getsizeof(args[0].kex_engine.x)

        # Store the bytes of the private value "x" before parsing newkeys message
        x_bytes_before = (x_size * ctypes.c_uint8).from_address(x_address)

        # Executes the Paramiko _parse_newkeys function
        func(*args, **kwargs)

        # The kex_engine is being set to "None"
        print("kex_engine is None => ", args[0].kex_engine is None)
    return inner

# Patch the _parse_newkeys function
paramiko.Transport._handler_table[paramiko.common.MSG_NEWKEYS] = \
    patch_parse_newkeys(paramiko.Transport._parse_newkeys)

with paramiko.SSHClient() as ssh:
    ssh.load_system_host_keys()
    ssh.connect("192.168.1.50", 22, "user", "password", disabled_algorithms={
        # In this example, we focus on the "diffie-hellman-group14-sha256" kex engine
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
    })

    # Execute a simple command
    _, stdout, _ = ssh.exec_command("uname -a")
    print(stdout.read().decode())

# Get the same amount of bytes stored at the same address of the value we
# previously obtained
x_bytes_after = (x_size * ctypes.c_uint8).from_address(x_address)

print(bytearray(x_bytes_before).hex())
print(bytearray(x_bytes_after).hex())
print("Equal = ", all(x == y for x, y in zip(x_bytes_before, x_bytes_after)))
