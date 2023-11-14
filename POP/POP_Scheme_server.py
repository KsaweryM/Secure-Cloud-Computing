from POP_Scheme_tools import *

class Server:
    def create_proof(self, tagged_file, H):
        PUBLIC_KEY = H[0]
        x_c = H[1]
        value = H[2]
        psi = []
        psi.append((mcl_zero, value))
        for (m, t) in tagged_file:
            psi.append((m, PUBLIC_KEY * t))
        PROOF = lagrange_interpolation(psi, x_c)
        return PROOF

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12347)
server_socket.bind(server_address)
server_socket.listen(1)

print("Waiting for a connection...")
connection, client_address = server_socket.accept()

try:
    print("Connected to", client_address)


    H, tagged_file = receive_object(connection)

    server = Server()
    PROOF = server.create_proof(tagged_file, H)

    send_object(connection, PROOF)
finally:
    connection.close()
