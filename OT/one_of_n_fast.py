import sys
from one_of_two import Client_1_Of_2, Server_1_Of_2
import random
import os
from json_utility import *

def pseudo_random(key: bytes, nr_bytes: int):
    random.seed(key)
    return random.randbytes(nr_bytes)

def int_to_bits(n, nr_bits):
    bits = [int(bit) for bit in bin(n)[2:]]
    while (len(bits) < nr_bits):
        bits = [0] + bits
    return bits

def byte_xor(b1, b2):
    return bytes([_a ^ _b for _a, _b in zip(b1, b2)])

class Server:
    __messages = None
    __log2_nr_messages = None
    __message_length = None
    __list_of_pairs_of_keys = None
    __key_length = None

    def transfer_init(self, messages: bytes, log2_nr_messages: int, message_length: int, key_length: int):
        self.__messages = messages
        self.__log2_nr_messages = log2_nr_messages
        self.__message_length = message_length
        self.__key_length = key_length
        self.__list_of_pairs_of_keys = [(random.randbytes(self.__key_length), random.randbytes(self.__key_length))
                                        for _ in range(self.__log2_nr_messages)]

    def get_list_of_pairs_of_keys(self):
        return self.__list_of_pairs_of_keys

    def get_encrypted_messages(self):
        encrypted_messages = []
        for message_index, message in enumerate(self.__messages):
            encrypted_message = message

            for bit_index, bit in enumerate(int_to_bits(message_index, self.__log2_nr_messages)):
                key = self.__list_of_pairs_of_keys[bit_index][bit]
                encrypted_message = byte_xor(encrypted_message, pseudo_random(key, self.__message_length))

            encrypted_messages.append(encrypted_message)

        return encrypted_messages

if __name__ == "__main__":
    def path_to_file(directory, file_name):
        return os.path.join(os.getcwd(), directory, file_name)

    path_to_encryptions = path_to_file("data", "encryptions.json")

    seed = b'seed'

    server = None

    log2_nr_messages = 3
    message_length = 5
    nr_messages = 2 ** log2_nr_messages

    messages = None
    encrypted_messages = None
    list_of_pairs_of_keys = None

    client_index = 0
    client_keys = []

    path_to_A = path_to_file("data", "A.json")
    path_to_B = path_to_file("data", "B.json")
    path_to_encryptions = path_to_file("data", "encryptions.json")

    server = Server()
    client_1_of_2 = Client_1_Of_2(seed)
    server_1_Of_2 = Server_1_Of_2(seed)

    random.seed(0)

    if (server_1_Of_2):
        messages = [random.randbytes(message_length) for _ in range(nr_messages)]

        server.transfer_init(messages, log2_nr_messages, message_length, 3)

        list_of_pairs_of_keys = server.get_list_of_pairs_of_keys()
        encrypted_messages = server.get_encrypted_messages()

        save_to_json(path_to_encryptions, encrypted_messages)


    for index, key_index in enumerate(int_to_bits(client_index, log2_nr_messages)):
        print(f"{index}. round!\n")

        if (client_1_of_2):
            client_1_of_2.transfer_init(key_index)

        if (server_1_Of_2):
            server_1_Of_2.transfer_init(list_of_pairs_of_keys[index][0], list_of_pairs_of_keys[index][1])

        if (server_1_Of_2):
            input("Server: Click enter to generate A by server.")

            A = server_1_Of_2.get_A()
            save_to_json(path_to_A, A)

            print("Server: \"A\" file has been generated by server.")

        if (client_1_of_2):
            input("Client: \"A\" file is required. Click enter to process this file.")

            A = deserialize_G1(load_from_json(path_to_A))
            B = client_1_of_2.get_B(A)
            save_to_json(path_to_B, B)

            print("Client: Client generated \"B\" file.")

        if (server):
            input("Server: \"B\" file is required. Click enter to process this file.")
            B = deserialize_G1(load_from_json(path_to_B))
            encryption1, encryption2 = server_1_Of_2.send_encryptions(B)
            save_to_json(path_to_encryptions, (encryption1, encryption2))

            print("Server: Server generated \"encrypted message\".")

        if (client_1_of_2):
            input("Client: \"encrypted message\" is required. Click enter to process this file.")
            encryptions = deserialize_ciphertexts(load_from_json(path_to_encryptions))
            encryption1, encryption2 = encryptions

            decryption = client_1_of_2.receive_encryptions(encryption1, encryption2)
            client_keys.append(decryption)

    if (client_1_of_2):
        message = encrypted_messages[client_index]
        for key in client_keys:
            message = byte_xor(message, pseudo_random(key, message_length))

        print(f"{message=}")
        print(f"{messages[client_index]=}")

        assert(message == messages[client_index])