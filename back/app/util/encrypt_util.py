import binascii
import os
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ENCRYPTION_KEY").encode()

def encrypt(plain_text: str) -> str:
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode())
    return b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt(enc_text: str) -> str:
    try:
        data = b64decode(enc_text)
        nonce = data[:16]
        tag = data[16:32]
        ciphertext = data[32:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
    except (binascii.Error, ValueError):
        return enc_text
