from time import time
from hmac import HMAC
from hashlib import sha256

from pysecube import (Wrapper, PySEcubeException, HMACSHA256)

# import logging
# logging.basicConfig()
# logging.getLogger("pysecube").setLevel(logging.DEBUG)

HMAC_KEY_ID = 20
HMAC_KEY_BYTES = b"\x01\x02\x03\x04\x05\x06\x07\x08" + \
                 b"\x09\x10\x11\x12\x13\x14\x15\x16" + \
                 b"\x17\x18\x19\x20\x21\x22\x23\x24" + \
                 b"\x25\x26\x27\x28\x29\x30\x31\x32" # 32 byte key for HMAC

PYSECUBE_PIN = b"test"
MESSAGE = b"A" * pow(2, 8) # 256 bytes
N = 1000

def main():
    secube_wrapper = Wrapper(PYSECUBE_PIN)

    if secube_wrapper.key_exists(HMAC_KEY_ID):
        secube_wrapper.delete_key(HMAC_KEY_ID)

    secube_wrapper.add_key(HMAC_KEY_ID, b"HMACTestKey", HMAC_KEY_BYTES, 3600)
    secube_wrapper.crypto_set_time_now()

    secube_total_time = 0
    hmac_total_time = 0

    mac_value = None

    # Python built-in
    for i in range(N):
        t0 = time()
        mac = HMAC(HMAC_KEY_BYTES, MESSAGE, sha256).digest()
        t1 = time()
        
        # Ensure all MAC values returned are the same
        if mac_value is None:
            mac_value = mac
        else:
            assert(mac_value == mac)

        hmac_total_time += (t1 - t0)
    print("Hashlib done")

    # SEcube
    for _ in range(N):
        t0 = time()
        mac = HMACSHA256(secube_wrapper, HMAC_KEY_ID, MESSAGE).digest()
        t1 = time()
        
        # Ensure all MAC values returned are the same
        if mac_value is None:
            mac_value = mac
        else:
            assert(mac_value == mac)

        secube_total_time += (t1 - t0)
    print("SEcube done")

    secube_wrapper.delete_key(HMAC_KEY_ID)
    secube_wrapper.destroy()

    return (secube_total_time, hmac_total_time)

if __name__ == "__main__":
    (secube_total_time, hmac_total_time) = main()
    print("secube_total_time:", secube_total_time)
    print("hmac_total_time:", hmac_total_time)
