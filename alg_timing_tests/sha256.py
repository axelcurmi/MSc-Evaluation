from time import time
from hashlib import sha256

from pysecube import (Wrapper, PySEcubeException)

PYSECUBE_PIN = b"test"
MESSAGE = b"A" * pow(2, 8) # 256 bytes
N = 1000

def main():
    secube_wrapper = Wrapper(PYSECUBE_PIN)

    secube_wrapper.crypto_set_time_now()

    secube_total_time = 0
    hlib_total_time = 0

    digest_value = None

    # Python built-in
    for _ in range(N):
        t0 = time()
        digest = sha256(MESSAGE).digest()
        t1 = time()
        
        # Ensure all MAC values returned are the same
        if digest_value is None:
            digest_value = digest
        else:
            assert(digest_value == digest)

        hlib_total_time += (t1 - t0)
    print("Hashlib SHA256 done")

    # SEcube
    for _ in range(N):
        t0 = time()
        digest = secube_wrapper.sha256(MESSAGE)
        t1 = time()
        
        # Ensure all MAC values returned are the same
        if digest_value is None:
            digest_value = digest
        else:
            assert(digest_value == digest)

        secube_total_time += (t1 - t0)
    print("SEcube SHA256 done")

    secube_wrapper.destroy()

    return (secube_total_time, hlib_total_time)

if __name__ == "__main__":
    (secube_total_time, hlib_total_time) = main()
    print("secube_total_time:", secube_total_time)
    print("hlib_total_time:", hlib_total_time)
