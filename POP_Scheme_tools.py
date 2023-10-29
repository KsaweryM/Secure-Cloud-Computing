import random
import mcl
import socket
import pickle

from mcl import G1

mcl_zero = mcl.Fr()
mcl_zero.setInt(0)

def send_object(client_socket, data_to_send):
    try:
        # Serialize the object using pickle
        data_serialized = pickle.dumps(data_to_send)

        # Send the object size first
        data_size = len(data_serialized)
        client_socket.send(data_size.to_bytes(4, byteorder='big'))

        # Send the serialized data
        client_socket.sendall(data_serialized)
    except Exception as e:
        print("Error sending data:", str(e))

def receive_object(client_socket):
    try:
        # Receive the object size
        data_size_bytes = client_socket.recv(4)
        data_size = int.from_bytes(data_size_bytes, byteorder='big')

        # Receive the serialized data
        received_data = b""
        remaining_bytes = data_size
        while remaining_bytes > 0:
            chunk = client_socket.recv(min(remaining_bytes, 1024))
            if not chunk:
                break
            received_data += chunk
            remaining_bytes -= len(chunk)

        # Deserialize the received data using pickle
        received_object = pickle.loads(received_data)
        return received_object
    except Exception as e:
        print("Error receiving data:", str(e))

def execute_polynomial(polynomial, argument):
    value = mcl.Fr()
    for coefficient in polynomial:
        value = value * argument
        value = value + coefficient
    return value

def lagrange_interpolation(tagged_file, x):
    interpolation = mcl.G1()
    for point_1 in tagged_file:
        x_i, y_i = point_1
        multi = mcl.Fr()
        multi.setInt(1)
        for point_2 in tagged_file:
                x_j, _ = point_2
                if x_i != x_j:
                    multi *= (x - x_j) / (x_i - x_j)
        multi = y_i * multi
        interpolation += multi
    return interpolation