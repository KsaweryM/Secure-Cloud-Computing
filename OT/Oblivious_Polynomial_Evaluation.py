from mcl import Fr
import numpy as np
import sys
import socket
from one_of_n import Client_1_of_N, Server_1_of_N
from utilities import send, receive

def int_to_Fr(value: int):
    fr = Fr()
    fr.setInt(value)

    return fr

def calculate_value_for_polynomial(coefficients: list[Fr], argument: Fr) -> Fr:
    value = Fr()
    value.setInt(0)
    for coefficient in coefficients:
        value = value * argument
        value = value + coefficient
    return value

class Client:
    __d_p = None
    __k = None
    __m = None
    __n = None
    __N = None
    __alpha = None
    __xs = None
    __T = None

    def __init__(self, d_p: int, k: int, m: int):
        self.__d_p = d_p
        self.__k = k
        self.__m = m
        self.__n = self.__k * self.__d_p + 1
        self.__N = self.__n * self.__m

    def __get_polynomial_requests(self, alpha: int) -> list[int]:
        self.__alpha = alpha

        self.__T = np.random.choice(range(self.__N), self.__n, replace=False)
        self.__xs = [Fr.rnd() for _ in range(self.__N)]

        coefficients = [Fr.rnd() for _ in range(self.__k)]
        coefficients[-1].setInt(self.__alpha)

        return [((x_i, calculate_value_for_polynomial(coefficients, x_i)) if i in self.__T else (x_i, Fr.rnd())) for i, x_i in enumerate(self.__xs)]

    def __lagrange_interpolation(self, polynomial_points, argument: Fr):
        interpolation = Fr()
        interpolation.setInt(0)

        for first_sample in polynomial_points:
            x_i, y_i = first_sample
            multi = Fr()
            multi.setInt(1)

            for second_sample in polynomial_points:
                    x_j, _ = second_sample
                    if x_i != x_j:
                        multi *= (argument - x_j) / (x_i - x_j)

            multi = y_i * multi
            interpolation += multi

        return interpolation

    def __get_polynomial_value_for_alpha(self, polynomial_samples):
        return self.__lagrange_interpolation(polynomial_samples, int_to_Fr(0))

    def execute_protocol(self, TCP_socket: socket):
        polynomial_requests = self.__get_polynomial_requests(alpha)

        send(TCP_socket, polynomial_requests)

        client_1_of_N = Client_1_of_N(seed)

        polynomial_samples = []

        for index in self.__T:
            polynomial_samples.append(client_1_of_N.execute_protocol(index, client_socket))

        return self.__get_polynomial_value_for_alpha(polynomial_samples)

class Server:
    __d_p = None
    __k = None
    __bivariate_polynomial = None

    def __init__(self, k: int, private_polynomial: list[Fr]):
        self.__d_p = len(private_polynomial) - 1
        self.__k = k

        polynomial_Px = [Fr.rnd() for _ in range(self.__d_p * self.__k)]
        polynomial_Px[-1].setInt(0)

        self.__bivariate_polynomial = [polynomial_Px, private_polynomial]

    def __calculate_value_for_bivariate_polynomial(self, bivariate_polynomial: list[list[Fr]], arguments: list[Fr]) -> Fr:
        value = Fr()
        value.setInt(0)

        for polynomial, argument in zip(bivariate_polynomial, arguments):
            value = value + calculate_value_for_polynomial(polynomial, argument)

        return value

    def __get_polynomial_samples(self, arguments: list[list[Fr]]):
        return [(argument[0], self.__calculate_value_for_bivariate_polynomial(self.__bivariate_polynomial, argument)) for argument in arguments]

    def execute_protocol(self, TCP_socket: socket):
        polynomial_requests = receive(TCP_socket)
        polynomial_samples = self.__get_polynomial_samples(polynomial_requests)
        server_1_of_N = Server_1_of_N(seed)

        for _ in range(n):
            server_1_of_N.execute_protocol(polynomial_samples, TCP_socket)

if __name__ == "__main__":
    if (len(sys.argv) != 4):
        raise ValueError("Invalid number of args.")

    IP = sys.argv[2]
    port = int(sys.argv[3])

    seed = b"test"
    server_polynomial = [int_to_Fr(2), int_to_Fr(0), int_to_Fr(0)]

    d_p = len(server_polynomial) - 1
    k = 3
    n = d_p * k + 1
    m = 10
    alpha = 10

    if (sys.argv[1] == "server"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((IP, port))
            server_socket.listen()
            client_socket, _ = server_socket.accept()

            server = Server(k, server_polynomial)
            server.execute_protocol(client_socket)

    elif (sys.argv[1] == "client"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((IP, port))

            client = Client(d_p, k, m)
            value = client.execute_protocol(client_socket)
            print(value)

    else:
        raise ValueError("Invalid argument.")