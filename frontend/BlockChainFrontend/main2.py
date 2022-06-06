import json
import sqlite3
import requests
from BlockChainFrontend.wallet.wallet import Wallet
from BlockChainFrontend.db import Database

base_url = 'http://localhost:5000'
port = 0


def getWallet():
    database = Database("wallet.db")
    data = database.getData()
    if len(data) == 0:
        wallet = Wallet(data[0], data[1])
        return wallet
    else:
        wallet = Wallet()
        database.insert(wallet.serializePrivate(), wallet.getSerializedKey())
        return wallet


wallet = getWallet()

while True:
    print("1 - get chain")
    print("2 - upload document")
    print("3 - generate network")
    print("4 - join network")
    print("0 - quit")
    action = int(input("what do you want to do: "))
    if action == 0:
        break
    elif action == 1:
        if port == 0:
            print("you do not have a network")
        else:
            r = requests.post(url=base_url + "/blockchain/get_chain", json={'port': port})
            print(r.json())
            for block in r.json():
                if block['data']:
                    for document in block['data']:
                        # print(wallet.decrypt(wallet.key, document['data']))
                        print(document['data'])

    elif action == 2:
        data = input("enter data you want to save: ")
        # encData = wallet.encrypt(data)
        signature = wallet.sign(data)

        if port == 0:
            print("you do not have a network")
        else:
            requests.post(url=base_url + "/blockchain/upload", json={'port': port,
                                                                     'document': {'publicKey': wallet.eccPublicKey,
                                                                                  'data': data,
                                                                                  'signature': signature}})
    elif action == 3:
        if port == 0:
            res = requests.get(url=base_url + "/blockchain/generate")
            port = res.json()['rootPort']
            print("your new network is on: " + str(port))
        else:
            print("you already have a network")
    elif action == 4:
        port = int(input("What is your port: "))
        print("your new network is on: " + str(port))
    # elif action == 5:
    #     wallet = Wallet
    #     data = {'data': 'data'}
    #     encData = wallet.encrypt(json.dumps(data))
    #     signature = wallet.sign(encData)
    #     print({'publicKey': wallet.eccPublicKey, 'data': encData, 'signature': signature})
    #     decJsonData = wallet.decrypt(wallet.key, wallet.nonce, encData).decode('utf-8')
    #     decData = json.loads(decJsonData)
    #     print(decData)
