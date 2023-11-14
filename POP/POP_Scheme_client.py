from POP_Scheme_tools import *

class Client:
    PF = None

    def read_file(self, path, chunk_size):
        divided_file = []
        nr_chunks = 0
        with open(path, 'rb') as file:
            while True:
                byte = file.read(chunk_size)
                if not byte:
                    break
                nr_chunks += 1
                divided_file.append(int.from_bytes(byte, "big"))
        return divided_file, hash(path.encode("utf-8")), nr_chunks

    def PRNG(self, secret_key, file_ID, index):
        random.seed(hash(secret_key.getStr()) + hash(file_ID) + hash(index))
        random_value = mcl.Fr()
        random_value.setInt(random.randint(0, 2**32))
        return random_value

    def create_polynomial(self, secret_key, file_ID, nr_chunks):
        polynomial = []
        for i in range(0, nr_chunks + 1):
            polynomial.append(self.PRNG(secret_key, file_ID, i))
        return polynomial

    def print_polynomial(self, polynomial):
        for i, coefficient in enumerate(polynomial):
            print(f"a_{i} = {coefficient.getStr()}")

    def print_tagged_file(self, tagged_file):
        for i, (m, t) in enumerate(tagged_file):
            print(f"m_{i} = {m.getStr()}, t = {t.getStr()}")

    def tag_file(self, file, polynomial):
        tagged_file = []
        for i in range(len(file)):
            fr_file = mcl.Fr()
            fr_file.setInt(file[i])
            tagged_file.append((fr_file, execute_polynomial(polynomial, fr_file)))
        return tagged_file

    def create_challenge(self, file_name):
        chunk_size = 2
        file, file_ID, nr_chunks = self.read_file(file_name, chunk_size)
        secret_key = mcl.Fr()
        secret_key.setByCSPRNG()
        G = G1.hashAndMapTo(b"genQ")
        PUBLIC_KEY = G * secret_key
        poly = self.create_polynomial(secret_key, file_ID, nr_chunks)
        tagged_file = self.tag_file(file, poly)
        x_c = mcl.Fr()
        x_c.setByCSPRNG()
        H = (PUBLIC_KEY, x_c, PUBLIC_KEY * (execute_polynomial(poly, mcl_zero)))
        PF = PUBLIC_KEY * execute_polynomial(poly, x_c)
        self.PF = PF
        return H, tagged_file

    def verify_proof(self, PROOF):
        return self.PF == PROOF

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12347)

try:
    client_socket.connect(server_address)

    client = Client()
    H, tagged_file = client.create_challenge("text.txt")

    send_object(client_socket, (H, tagged_file))

    PROOF = receive_object(client_socket)

    print(client.verify_proof(PROOF))
finally:
    client_socket.close()