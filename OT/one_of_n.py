from json_utility import *
from mcl import Fr, G1
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import sys
import os

class Client:
    __GENERATOR = None
    __alfa  = None
    __index = None

    def __init__(self, seed):
        self.__GENERATOR = G1.hashAndMapTo(seed)

    def choose_omega(self, index : int, Rs : list[G1]) -> G1:
        self.__index = index
        self.__alfa  = Fr.rnd()

        return Rs[self.__index] * self.__alfa

    def decode(self, encrypted_blocks: list[tuple[bytes | bytearray | memoryview, bytes]]) -> str:
        iv, ciphertext = encrypted_blocks[self.__index]
        cipher = AES.new(((self.__GENERATOR * self.__alfa).getStr())[:16], AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ciphertext), AES.block_size)

        return pt.decode()

class Server:
    __GENERATOR = None
    __blocks    = None
    __rs        = None
    __Rs        = None
    __keys      = None

    def __init__(self, seed):
        self.__GENERATOR = G1.hashAndMapTo(seed)

    def one_of_two_n(self, blocks):
        self.__blocks = blocks
        self.__rs     = None
        self.__Rs     = None
        self.__keys   = None

    def get_Rs(self) -> list[G1]:
        self.__rs = [Fr.rnd() for _ in self.__blocks]
        self.__Rs = [self.__GENERATOR * r for r in self.__rs]

        return self.__Rs

    def create_keys(self, omega: G1) -> list[bytes]:
        one = Fr.setHashOf(b'1') / Fr.setHashOf(b'1')
        self.__keys = [(omega * (one / r)).getStr()[:16] for r in self.__rs]

    def get_encrypted_blocks(self) -> list[tuple[bytes | bytearray | memoryview, bytes]]:
        assert(self.__keys)

        encrypted_blocks = []
        for key, message in zip(self.__keys, self.__blocks):
            cipher = AES.new(key, AES.MODE_CBC)

            encrypted_block = cipher.encrypt(pad(message, AES.block_size))
            encrypted_blocks.append((cipher.iv, encrypted_block))
        return encrypted_blocks

def path_to_file(directory, file_name):
    return os.path.join(os.getcwd(), directory, file_name)

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        raise ValueError("Invalid number of args.")

    seed = b'seed'
    blocks = [b'Hello ', b'there!', b'General ', b'Kenobi!']
    index = 1

    client = None
    server = None

    if (sys.argv[1] == "client"):
        client = Client(seed)
    elif (sys.argv[1] == "server"):
        server = Server(seed)
    else:
        raise ValueError("Invalid argument.")

    if server:
        server.one_of_two_n(blocks)
        Rs = server.get_Rs()
        save_to_json(path_to_file("data", "rand.json"), Rs)
        print("\"rand.json\" has been added.")

    if client:
        input("add \"rand.json\".")
        serialized_rand = load_from_json(path_to_file("data", "rand.json"))
        deserialized_rand = deserialize_rand(serialized_rand)
        omega = client.choose_omega(index, deserialized_rand)
        save_to_json(path_to_file("data", "w.json"), omega)
        print("\"w.json\" has been added.")

    if server:
        input("add \"w.json\".")
        serialized_omega = load_from_json(path_to_file("data", "w.json"))
        deserialized_omega = deserialize_G1(serialized_omega)
        server.create_keys(deserialized_omega)
        encrypted_blocks = server.get_encrypted_blocks()
        save_to_json(path_to_file("data", "ciphertexts.json"), encrypted_blocks)
        print("\"ciphertexts.json\" has been added.")

    if client:
        input("add \"ciphertexts.json\".")
        serialized_encrypted_blocks = load_from_json(path_to_file("data", "ciphertexts.json"))
        deserialized_encrypted_blocks = deserialize_ciphertexts(serialized_encrypted_blocks)
        decoded_block = client.decode(deserialized_encrypted_blocks)

        print(decoded_block)