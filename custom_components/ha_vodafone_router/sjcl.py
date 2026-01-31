import binascii

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class SJCL:
    DEFAULT_SJCL_ITERATIONS = 1000
    DEFAULT_SJCL_KEYSIZEBITS = 128
    DEFAULT_SJCL_TAGLENGTH = 128  # bits

    @staticmethod
    def pbkdf2(
        password: str, salt_hex: str, iterations: int, key_size_bits: int
    ) -> str:
        salt = binascii.unhexlify(salt_hex)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_size_bits // 8,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )

        key = kdf.derive(password.encode())
        return binascii.hexlify(key).decode()

    @staticmethod
    def ccm_encrypt(
        derived_key_hex: str,
        plaintext: str,
        iv_hex: str,
        auth_data: str,
        tag_len_bits: int,
    ) -> str:
        key = binascii.unhexlify(derived_key_hex)
        iv = binascii.unhexlify(iv_hex)

        aesccm = AESCCM(key, tag_length=tag_len_bits // 8)

        ciphertext = aesccm.encrypt(
            iv,
            plaintext.encode(),
            auth_data.encode(),
        )

        return binascii.hexlify(ciphertext).decode()

    @staticmethod
    def ccm_decrypt(
        derived_key_hex: str,
        cipher_hex: str,
        iv_hex: str,
        auth_data: str,
        tag_len_bits: int,
    ) -> str:
        key = binascii.unhexlify(derived_key_hex)
        iv = binascii.unhexlify(iv_hex)
        ciphertext = binascii.unhexlify(cipher_hex)

        aesccm = AESCCM(key, tag_length=tag_len_bits // 8)

        plaintext = aesccm.decrypt(
            iv,
            ciphertext,
            auth_data.encode(),
        )

        return plaintext.decode()
