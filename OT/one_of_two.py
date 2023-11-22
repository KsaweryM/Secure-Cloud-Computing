from utilities import *
from mcl import Fr, G1
import sys

class Client_1_Of_2:
    __GENERATOR = None
    __b = None
    __index = None
    __key = None

    def __init__(self, seed: bytes):
        self.__GENERATOR = G1.hashAndMapTo(seed)

    def transfer_init(self, index: int):
        self.__b = Fr.rnd()
        self.__index = index

    def get_B(self, A: G1):
        B = None

        if (self.__index == 0):
            B = self.__GENERATOR * self.__b
        elif (self.__index == 1):
            B = A + self.__GENERATOR * self.__b
        else:
            raise ValueError("Invalid index.")

        self.__key = hash_G1_to_bytes(A * self.__b)

        return B

    def receive_encryptions(self, encryption1, encryption2):
        encryption = None

        if (self.__index == 0):
            encryption = encryption1
        elif (self.__index == 1):
            encryption = encryption2
        else:
            raise ValueError("Invalid index.")

        return decrypt_message(encryption, self.__key)

class Server_1_Of_2:
    __GENERATOR = None
    __a = None
    __M_0 = None
    __M_1 = None

    def __init__(self, seed: bytes):
        self.__GENERATOR = G1.hashAndMapTo(seed)

    def transfer_init(self, M_0: bytes, M_1: bytes):
        self.__a = Fr.rnd()
        self.__M_0 = M_0
        self.__M_1 = M_1

    def get_A(self) -> G1:
        return self.__GENERATOR * self.__a

    def get_encryptions(self, B: G1):
        K_0 = hash_G1_to_bytes(B * self.__a)
        K_1 = hash_G1_to_bytes((B - self.__GENERATOR * self.__a) * self.__a)

        return (encrypt_message(self.__M_0, K_0), encrypt_message(self.__M_1, K_1))

def execute_server(seed: int, first_message: bytes, second_message: bytes, IP: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((IP, port))
        server_socket.listen()
        client_socket, _ = server_socket.accept()

        server = Server_1_Of_2(seed)
        server.transfer_init(first_message, second_message)

        A = server.get_A()
        send(client_socket, A)

        B = receive(client_socket)
        encryption1, encryption2 = server.get_encryptions(B)
        send(client_socket, (encryption1, encryption2))


def execute_client(seed: int, client_index: int, IP: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((IP, port))

        client = Client_1_Of_2(seed)
        client.transfer_init(client_index)

        A = receive(client_socket)

        B = client.get_B(A)
        send(client_socket, B)
        encryption1, encryption2 = receive(client_socket)

        decryption = client.receive_encryptions(encryption1, encryption2)
        print(f"Client: message: \"{decryption}\".")

if __name__ == "__main__":
    if (len(sys.argv) != 4):
        raise ValueError("Invalid number of args.")

    IP = sys.argv[2]
    port = int(sys.argv[3])

    seed = b'seed'
    client_index = 1
    first_message = b'Hello'
    second_message =  b'There'

    if (sys.argv[1] == "server"):
        execute_server(seed, first_message, second_message, IP, port)
    elif (sys.argv[1] == "client"):
        execute_client(seed, client_index, IP, port)
    else:
        raise ValueError("Invalid argument.")