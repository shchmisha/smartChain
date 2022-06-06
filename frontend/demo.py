import json
import random
import socket
import sqlite3
from struct import pack

import requests
from BlockChainFrontend.wallet.wallet import Wallet
from frontend.db import Database

chains = {}
nodes = {}


def send_request(data, port, host):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((host, port))
    length = pack('<L', len(json.dumps(data).encode('utf-8')))
    client_sock.sendall(length)
    client_sock.sendall(json.dumps(data).encode('utf-8'))
    recieved_data = json.loads(client_sock.recv(4096).decode('utf-8'))
    client_sock.close()
    return recieved_data


def getKey():
    database = Database("keys.db")
    data = database.getData()
    print(data)
    if len(data) != 0:
        chains[data[0][0]] = data[0][1]
    else:
        name = input("Enter new chain name: ")
        port = 5000
        response = send_request({'route': 'create_chain'}, port, 'localhost')
        chains[name] = response['chain_token']
        nodes[response['chain_token']] = response['chain_nodes']
        database.insert(response['chain_token'], name)


getKey()

while True:
    print("1 - get chain")
    print("2 - upload document")
    print("3 - create chain")
    print("4 - get document")
    print("0 - quit")

    action = int(input("what do you want to do: "))
    if action == 0:
        break
    elif action == 1:
        chain_name = input("chain name: ")
        chain_token = chains[chain_name]
        data = send_request({'route': 'get_data', 'chain_token': chain_token},
                            nodes[chain_token][random.randint(0, len(nodes[chain_token]) - 1)], 'localhost')
        for doc in data['data']:
            print(doc)

    elif action == 2:
        chain_name = input("chain name: ")
        chain_token = chains[chain_name]
        data = input("enter data you want to save: ")

        send_request({'route': 'upload_data', 'data': {'data_token': data}, 'chain_token': chain_token},
                     nodes[chain_token][random.randint(0, len(nodes[chain_token]) - 1)], 'localhost')

    elif action == 3:
        name = input("Enter new chain name: ")
        port = 5000
        response = send_request({'route': 'create_chain'}, port, 'localhost')
        chains[name] = response['chain_token']
        nodes[response['chain_token']] = response['chain_nodes']

    elif action == 4:
        chain_name = input("chain name: ")
        chain_token = chains[chain_name]
        doc_name = input("enter document name: ")
