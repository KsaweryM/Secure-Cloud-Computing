import random
import mcl

from mcl import GT
from mcl import G2
from mcl import G1
from mcl import Fr

# client

z = 2
secret_key = mcl.Fr()
secret_key.setByCSPRNG()

G = G1.hashAndMapTo(b"genQ")
PUBLIC_KEY = G * secret_key

def PRNG(secret_key, file_ID, index):
    random.seed(hash(secret_key.getStr()) + hash(file_ID) + hash(index))
    random_value = mcl.Fr()
    random_value.setInt(random.randint(0, 2**32))
    return random_value

def create_polynomial(secret_key, file_ID):
    polynomial = []
    for i in range(0, z + 1):
        polynomial.append(PRNG(secret_key, file_ID, i))
    return polynomial

def print_polynomial(polynomial):
    for point in polynomial:
        print(f"a = {point.getStr()}")

def print_tagged_file(polynomial):
    for point in polynomial:
        print(f"m = {point[0].getStr()}, t = {point[1].getStr()}")

def fr_power(argument, exponent):
    value = mcl.Fr()
    value.setInt(1)
    for i in range(exponent):
        value = value * argument
    return value

def execute_polynomial(polynomial, argument):
    value = mcl.Fr()
    for i in range(0, len(polynomial)):
        value += fr_power(argument, i) * polynomial[i]
    return value

def random_file():
    file = []
    for i in range(z + 1):
        file.append(random.randint(0, 2**32))
    return file

def tag_file(file, polynomial):
    tagged_file = []
    for i in range(len(file)):
        fr_file = mcl.Fr()
        fr_file.setInt(file[i])
        tagged_file.append((fr_file, execute_polynomial(poly, fr_file)))
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

file = random_file()
file_ID = hash("hello.txt")

poly = create_polynomial(secret_key, file_ID)

tagged_file = tag_file(file, poly)

x_c = mcl.Fr()
x_c.setByCSPRNG()

mcl_zero = mcl.Fr()
mcl_zero.setInt(0)

H = (PUBLIC_KEY, x_c, PUBLIC_KEY * (execute_polynomial(poly, mcl_zero)))

Pf = PUBLIC_KEY * execute_polynomial(poly, x_c)

# client end

#server

psi = []
psi.append((mcl_zero, H[2]))

for (m, t) in tagged_file:
    psi.append((m, PUBLIC_KEY * t))

RESPONSE = lagrange_interpolation(psi, x_c)
print(RESPONSE.getStr())

print(Pf == RESPONSE)