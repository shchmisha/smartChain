import hashlib
import json

def cryptoHash(*args):
    stringData = sorted(map(lambda data: json.dumps(data), args))
    joinedData = ''.join(stringData)

    return hashlib.sha256(joinedData.encode('utf-8')).hexdigest()
