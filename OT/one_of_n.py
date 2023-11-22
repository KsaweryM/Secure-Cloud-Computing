from utilities import *
from mcl import Fr, G1
import sys

class Client_1_of_N:
    __GENERATOR = None
    __alfa  = None
    __index = None

    def __init__(self, seed: bytes):
        self.__GENERATOR = G1.hashAndMapTo(seed)

    def __choose_omega(self, index : int, Rs : list[G1]) -> G1:
        self.__index = index
        self.__alfa  = Fr.rnd()

        return Rs[self.__index] * self.__alfa

    def __decode(self, encrypted_blocks) -> str:
        return decrypt_message(encrypted_blocks[self.__index], hash_G1_to_bytes(self.__GENERATOR * self.__alfa))

    def execute_protocol(self, index: int, TCP_socket: socket) -> any:
        Rs = receive(TCP_socket)
        omega = self.__choose_omega(index, Rs)
        send(TCP_socket, omega)
        encrypted_blocks = receive(TCP_socket)
        decoded_block = self.__decode(encrypted_blocks)

        return pickle.loads(decoded_block)


class Server_1_of_N:
    __GENERATOR = None
    __blocks    = None
    __rs        = None
    __Rs        = None
    __keys      = None

    def __init__(self, seed: bytes):
        self.__GENERATOR = G1.hashAndMapTo(seed)

    def __get_Rs(self) -> list[G1]:
        self.__rs = [Fr.rnd() for _ in self.__blocks]
        self.__Rs = [self.__GENERATOR * r for r in self.__rs]

        return self.__Rs

    def __create_keys(self, omega: G1) -> list[bytes]:
        one = Fr.setHashOf(b'1') / Fr.setHashOf(b'1')
        self.__keys = [hash_G1_to_bytes(omega * (one / r)) for r in self.__rs]

    def __get_encrypted_blocks(self):
        assert(self.__keys)

        encrypted_blocks = []
        for key, message in zip(self.__keys, self.__blocks):
            encrypted_blocks.append(encrypt_message(message, key))

        return encrypted_blocks

    def execute_protocol(self, blocks: list, TCP_socket: socket):
        serialised_blocks = [pickle.dumps(block) for block in blocks]
        self.__blocks = serialised_blocks
        Rs = self.__get_Rs()
        send(TCP_socket, Rs)
        omega = receive(TCP_socket)
        self.__create_keys(omega)
        encrypted_blocks = self.__get_encrypted_blocks()
        send(TCP_socket, encrypted_blocks)

if __name__ == "__main__":
    if (len(sys.argv) != 4):
        raise ValueError("Invalid number of args.")

    IP = sys.argv[2]
    port = int(sys.argv[3])

    seed = b'seed'
    blocks = [b'Hello ', b'there!', b'General ', b'Kenobi!']
    index = 1

    if (sys.argv[1] == "server"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((IP, port))
            server_socket.listen()
            client_socket, _ = server_socket.accept()

            server = Server_1_of_N(seed)
            server.execute_protocol(blocks, client_socket)

    elif (sys.argv[1] == "client"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((IP, port))
            client = Client_1_of_N(seed)

            output = client.execute_protocol(index, client_socket)
            print(output)



    else:
        raise ValueError("Invalid argument.")