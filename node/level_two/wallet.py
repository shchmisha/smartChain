import base64
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature, decode_dss_signature
)

from Cryptodome.Cipher import AES
from secrets import token_bytes


class Wallet:
    def __init__(self, eccPrivateKey = None, skey = None):
        self.eccPrivateKey = self.getPrivate(eccPrivateKey)
        self.eccPublicKey = self.getPublic()
        self.key = self.getKey(skey)
        # cipher = AES.new(self.key, AES.MODE_ECB)
        # self.nonce = cipher.nonce

    def getPrivate(self, serPrivateKey):
        if serPrivateKey:
            return serialization.load_pem_private_key(serPrivateKey.encode("utf-8"), None, default_backend())
        else:
            return ec.generate_private_key(
                ec.SECP256K1(),
                default_backend()
            )

    def getPublic(self):
        return self.eccPrivateKey.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def getKey(self, skey):
        if skey:
            return base64.b64decode(skey)
        else:
            return token_bytes(16)

    def getSerializedKey(self):
        return str(base64.b64encode(self.key),'utf-8')

    def sign(self, data):
        return decode_dss_signature(self.eccPrivateKey.sign(
            # json.dumps(data).encode('utf-8'),
            json.dumps(data).encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        ))

    def serializePrivate(self):
        return self.eccPrivateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

    @staticmethod
    def verify(publicKey, data, signature):

        deserialized_public_key = serialization.load_pem_public_key(
            publicKey.encode('utf-8'),
            default_backend()
        )

        (r, s) = signature
        # print(r, s)
        try:
            deserialized_public_key.verify(
                encode_dss_signature(r, s),
                json.dumps(data).encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False

    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(json.dumps(data).encode('utf-8'))
        return ciphertext.decode('latin1')

    @staticmethod
    def decrypt(key, cipherText):
        cipher = AES.new(key, AES.MODE_ECB)
        text = cipher.decrypt(cipherText.encode('latin1'))
        return text.decode('utf-8')

if __name__ == '__main__':
    wallet = Wallet()
    # data = {'data': 'data'}
    # encData = wallet.encrypt(data)
    get_data_script = {'route': 'get_data', "instruction": "$index = 0 foreach blockchain $var { blockchain return $var \"document\"+$index $index = $index + 1 }"}
    get_data = {'script': get_data_script, 'signature': wallet.sign(get_data_script), 'public_key': wallet.eccPublicKey}
    # signature = wallet.sign(get_data)
    # get_data['pk_sign']=signature
    #
    #
    # new_data = dict(get_data)
    # sign = new_data['pk_sign']
    # new_data.pop('pk_sign')
    # print(wallet.verify(wallet.eccPublicKey, new_data, sign))
    # print(get_data)
    # print(new_data)
    sign1= wallet.sign("data")
    sign2=wallet.sign("data")
    print(sign1, sign2)
    # print({'publicKey': wallet.eccPublicKey, 'data': encData, 'signature': signature})
    # decJsonData = wallet.decrypt(wallet.key, wallet.nonce, encData)
    # print(decJsonData)
