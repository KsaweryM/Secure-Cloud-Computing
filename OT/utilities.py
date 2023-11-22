import json
from typing import Any, Union
from mcl import G1
import socket
import pickle
import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def send(TCP_socket: socket, message: bytes):
    encoded_msg = pickle.dumps(message)
    packed_msg = struct.pack('>I', len(encoded_msg)) + encoded_msg

    TCP_socket.sendall(packed_msg)

def recvall(TCP_socket: socket, nr_bytes: int):
    received_bytes = bytearray()
    while len(received_bytes) < nr_bytes:
        packet = TCP_socket.recv(nr_bytes - len(received_bytes))
        if not packet:
            return None

        received_bytes.extend(packet)

    return received_bytes

def receive(TCP_socket: socket):
    packed_nr_bytes_to_receive = recvall(TCP_socket, 4)
    if not packed_nr_bytes_to_receive:
        return None

    nr_bytes_to_receive = struct.unpack('>I', packed_nr_bytes_to_receive)[0]

    packed_message = recvall(TCP_socket, nr_bytes_to_receive)
    message = pickle.loads(packed_message)

    return message

def custom_encoder(obj: Any) -> Union[str, bytes]:
    if hasattr(obj, 'getStr'):
        return obj.getStr()
    elif isinstance(obj, bytes):
        return obj.decode('latin-1')
    raise TypeError("Object of unsupported type")


def save_to_json(file_path: str, value: Any) -> None:
    with open(file_path, 'w') as json_file:
        json_file.write(json.dumps(value, default=custom_encoder))


def load_from_json(file_path: str) -> Any:
    with open(file_path, 'r') as file:
        return json.load(file)

def deserialize_rand(data):
    res = []
    for rand in data:
        rand_ = G1()
        rand_.setStr(bytes(rand, 'latin-1'))
        res.append(rand_)
    return res

def deserialize_G1(data: str):
    g = G1()
    g.setStr(bytes(data, 'latin-1'))
    return g

def deserialize_keys(data):
    return [bytes(key, 'latin-1') for key in data]

def deserialize_ciphertexts(data):
    return [(bytes(iv, 'latin-1'), bytes(ct, 'latin-1')) for iv, ct in data]

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