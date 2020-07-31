import hashlib

def generate_md5(filename):
    with open(filename, "rb") as f:
        data = f.read()
        return hashlib.md5(data).hexdigest()
    return -1
