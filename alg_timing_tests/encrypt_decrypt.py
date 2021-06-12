from time import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from pysecube import (Wrapper,
                      ALGORITHM_AES,
                      FEEDBACK_CTR,
                      MODE_ENCRYPT,
                      MODE_DECRYPT)

# Use key with ID 10 stored in the SEcube device
AES_KEY_ID = 10
AES_KEY_BYTES = b"\x01\x02\x03\x04\x05\x06\x07\x08" + \
                b"\x01\x02\x03\x04\x05\x06\x07\x08" + \
                b"\x01\x02\x03\x04\x05\x06\x07\x08" + \
                b"\x01\x02\x03\x04\x05\x06\x07\x08" # 32 byte AES key
CTR_NONCE     = b"\xA1\xA2\xA3\xA4\xA5\xA6\xA7\xA8" + \
                b"\xA1\xA2\xA3\xA4\xA5\xA6\xA7\xA8" # 16 byte CTR nonce

PYSECUBE_PIN = b"test"
PLAINTEXT = b"A" * pow(2, 8) # 256 bytes
N = 1000

def main():
    secube_wrapper = Wrapper(PYSECUBE_PIN)
    secube_wrapper.crypto_set_time_now()

    if secube_wrapper.key_exists(AES_KEY_ID):
        secube_wrapper.delete_key(AES_KEY_ID)
    secube_wrapper.add_key(AES_KEY_ID, b"AESTestKey", AES_KEY_BYTES, 3600)

    openssl_engine = Cipher(algorithm = algorithms.AES(AES_KEY_BYTES),
                            mode = modes.CTR(CTR_NONCE),
                            backend = default_backend())

    secube_encrypter = secube_wrapper.get_crypter(
        ALGORITHM_AES, MODE_ENCRYPT | FEEDBACK_CTR, AES_KEY_ID, iv=CTR_NONCE
    )
    secube_decrypter = secube_wrapper.get_crypter(
        ALGORITHM_AES, MODE_DECRYPT | FEEDBACK_CTR, AES_KEY_ID, iv=CTR_NONCE
    )

    encryptor = openssl_engine.encryptor()
    decryptor = openssl_engine.decryptor()

    secube_total_time = 0
    openssl_total_time = 0

    # OpenSSL
    for _ in range(N):
        t0 = time()
        enc_out = encryptor.update(PLAINTEXT)
        dec_out = decryptor.update(enc_out)
        t1 = time()

        assert(PLAINTEXT == dec_out)
        openssl_total_time += (t1 - t0)
    print("OpenSSL done")

    # SEcube
    for _ in range(N):
        t0 = time()
        enc_out = secube_encrypter.update(PLAINTEXT)
        dec_out = secube_decrypter.update(enc_out)
        t1 = time()

        assert(PLAINTEXT == dec_out)
        secube_total_time += (t1 - t0)
    print("SEcube done")

    secube_wrapper.destroy()

    return (secube_total_time, openssl_total_time)

if __name__ == "__main__":
    (secube_total_time, openssl_total_time) = main()
    print("secube_total_time:", secube_total_time)
    print("openssl_total_time:", openssl_total_time)
