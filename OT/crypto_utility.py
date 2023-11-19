from mcl import G1
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def hash_G1_to_bytes(group_element: G1):
    return G1.hashAndMapTo(group_element.getStr()).getStr()[:16]

def encrypt_message(message, key: bytes):
    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_block = cipher.encrypt(pad(message, AES.block_size))
    return (cipher.iv, encrypted_block)

def decrypt_message(encrypted_message, key: bytes):
    iv, ciphertext = encrypted_message
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    return unpad(decrypted, AES.block_size)