import string

ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

BASE = len(ALPHABET)

def encode(num):
    """Преобразует положительное число в Base62"""
    if num == 0:
        return ALPHABET[0]
    arr = []
    while num:
        num, rem = divmod(num, BASE)
        arr.append(ALPHABET[rem])
    return ''.join(reversed(arr))

def decode(string):
    """Преобразует Base62 строку в число"""
    res = 0
    for char in string:
        res = res * BASE + ALPHABET.index(char)
    return res
