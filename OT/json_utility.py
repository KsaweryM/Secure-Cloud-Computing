import json
from typing import Any, Union
from mcl import Fr, G1

def custom_encoder(obj: Any) -> Union[str, bytes]:
    if hasattr(obj, 'getStr'):
        return obj.getStr()
    elif isinstance(obj, bytes):
        return obj.decode('latin-1')
    raise TypeError("Object of unsupported type")


def save_to_json(file_path: str, value: Any) -> None:
    with open(file_path, 'w') as json_file:
        json_file.write(json.dumps(value, default=custom_encoder))


def load_from_json(file_path: str) -> Any:
    with open(file_path, 'r') as file:
        return json.load(file)

def deserialize_rand(data):
    res = []
    for rand in data:
        rand_ = G1()
        rand_.setStr(bytes(rand, 'latin-1'))
        res.append(rand_)
    return res

def deserialize_w(data: str):
    g = G1()
    g.setStr(bytes(data, 'latin-1'))
    return g

def deserialize_keys(data):
    return [bytes(key, 'latin-1') for key in data]

def deserialize_ciphertexts(data):
    return [(bytes(iv, 'latin-1'), bytes(ct, 'latin-1')) for iv, ct in data]
