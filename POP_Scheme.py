import random
import mcl

from mcl import G1

def read_file(path, chunk_size):
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

def PRNG(secret_key, file_ID, index):
    random.seed(hash(secret_key.getStr()) + hash(file_ID) + hash(index))
    random_value = mcl.Fr()
    random_value.setInt(random.randint(0, 2**32))
    return random_value

def create_polynomial(secret_key, file_ID, nr_chunks):
    polynomial = []
    for i in range(0, nr_chunks + 1):
        polynomial.append(PRNG(secret_key, file_ID, i))
    return polynomial

def print_polynomial(polynomial):
    for i, coefficient in enumerate(polynomial):
        print(f"a_{i} = {coefficient.getStr()}")

def print_tagged_file(tagged_file):
    for i, (m, t) in enumerate(tagged_file):
        print(f"m_{i} = {m.getStr()}, t = {t.getStr()}")

def execute_polynomial(polynomial, argument):
    value = mcl.Fr()
    for coefficient in polynomial:
        value = value * argument
        value = value + coefficient
    return value

def tag_file(file, polynomial):
    tagged_file = []
    for i in range(len(file)):
        fr_file = mcl.Fr()
        fr_file.setInt(file[i])
        tagged_file.append((fr_file, execute_polynomial(polynomial, fr_file)))
    return tagged_file

def lagrange_interpolation(tagged_file, x):
    interpolation = mcl.G1()
    for point_1 in tagged_file:
        x_i, y_i = point_1
        multi = mcl.Fr()
        multi.setInt(1)
        for point_2 in tagged_file:
                x_j, y_j = point_2
                if x_i != x_j:
                    multi *= (x - x_j) / (x_i - x_j)
        multi = y_i * multi
        interpolation += multi
    return interpolation

chunk_size = 2
file, file_ID, nr_chunks = read_file("text.txt", chunk_size)
secret_key = mcl.Fr()
secret_key.setByCSPRNG()

G = G1.hashAndMapTo(b"genQ")
PUBLIC_KEY = G * secret_key

poly = create_polynomial(secret_key, file_ID, nr_chunks)
tagged_file = tag_file(file, poly)

x_c = mcl.Fr()
x_c.setByCSPRNG()

mcl_zero = mcl.Fr()
mcl_zero.setInt(0)

H = (PUBLIC_KEY, x_c, PUBLIC_KEY * (execute_polynomial(poly, mcl_zero)))

PF = PUBLIC_KEY * execute_polynomial(poly, x_c)
# client end

#server
psi = []
psi.append((mcl_zero, H[2]))

for (m, t) in tagged_file:
    psi.append((m, PUBLIC_KEY * t))

RESPONSE = lagrange_interpolation(psi, x_c)
print(PF.getStr())
print(RESPONSE.getStr())
#server end

#client
print(PF == RESPONSE)
#client end