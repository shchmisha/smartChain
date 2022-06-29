import json
import os
import random
import socket
import threading
import time
import secrets
from struct import pack, unpack

from node.level_two.looptest_vm import Interface
from node.level_two.wallet import Wallet

host = 'localhost'


# add a signalling where a test message is sent out and then if any node responds then they are activeand valid

# when a chain is created, it sends out a sync message
# innthat sync function, add the chain to the local sync

class SocketNode:
    def __init__(self, PORT, ROOT_PORT, HOST):
        # each new chain must have a root node for its own sub network
        self.chains = {}
        self.network_chains = {}
        self.lock = threading.Lock()
        self.connections = []
        self.peers = [ROOT_PORT]
        self.PORT = PORT
        self.ROOT_PORT = ROOT_PORT
        self.HOST = HOST
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))
        self.start_network()
        if self.PORT != self.ROOT_PORT:
            try:
                self.send_data_to_port(self.ROOT_PORT, {'route': 'sync_node','port': self.PORT})
            except:
                print("error syncing")

    def sync(self, newPort):
        if newPort not in self.peers:
            self.peers.append(newPort)
        # print(self.peers)

        data ={'route': 'sync_node_peers','peers': self.peers, 'root_peer': self.ROOT_PORT}
        self.send_data(data)
        return True

    def create_chain(self, n):

        user_wallet = Wallet()
        interface_wallet = Wallet()

        sign = user_wallet.sign("default_data")
        chain_token = str(secrets.token_bytes(16).hex())
        new_chain = Interface(user_wallet.eccPublicKey, self.PORT, self.PORT, chain_token,
                              interface_wallet.serializePrivate(),
                              interface_wallet.getSerializedKey(), self.HOST, self)
        self.chains[chain_token] = new_chain

        # introduce thread locks everywhere
        #
        # self.send_data({'chain_token': chain_token, 'route': 'add_chain', 'sign': sign, 'root_port': self.PORT, 'node_port': 5001})
        # self.send_data({'chain_token': chain_token, 'route': 'add_chain', 'sign': sign, 'root_port': self.PORT, 'node_port': 5002})
        #
        # self.send_data({'route': 'add_chain'})
        chain_nodes = []
        node = self.peers[random.randint(0, len(self.peers) - 1)]
        prev = None
        for i in range(n):
            while True:
                if node == self.PORT or node == prev:
                    node = self.peers[random.randint(0, len(self.peers)-1)]
                else:
                    break
            data = {'chain_token': chain_token, 'route': 'add_chain', 'user_pk': user_wallet.eccPublicKey,
                    'root_port': self.PORT, 'node_port': node, 'eccPrivateKey': interface_wallet.serializePrivate(),
                    'skey': "skey"}
            self.send_data(data)
            chain_nodes.append(self.PORT)
            prev = node
            node = self.peers[random.randint(0, len(self.peers)-1)]
        # print(chain_token)
        return chain_token, user_wallet.serializePrivate(), "default_data", chain_nodes

    def add_chain(self, user_pk, chain_token, root, eccPrivateKey, skey):
        # takes the token, sign and the root port
        # inside the vm, sends a request tothe root node to sync
        if chain_token not in self.chains.keys():
            new_chain = Interface(user_pk, root, self.PORT, chain_token, eccPrivateKey, skey, self.HOST, self)
            self.chains[chain_token] = new_chain
        # new_chain.start()


    def get_chain(self, chain_token):

        return self.chains[chain_token].blockchain_to_json()

    def sync_peers(self, newpeers, root_peer):
        # print("peers synced for "+str(self.PORT))
        self.peers = newpeers
        self.ROOT_PORT = root_peer


    def send_data(self, data):
        # self.lock.acquire()
        for peer in self.peers:
            if peer != self.PORT:
                self.send_data_to_port(peer, data)

    def send_data_to_port(self, port, data):

        length = pack('<L', len(json.dumps(data).encode('utf-8')))
        # print("sending", len(length))
        # print(len(json.dumps(data).encode('utf-8')))
        # length = str(len(json.dumps(data).encode('utf-8'))).encode('utf-8')
        # print("len", len(json.dumps(data).encode('utf-8')), json.dumps(data).encode('utf-8'))
        # self.lock.acquire()
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # later, ports will be replaced by other hosts, therefore
            client_sock.connect((self.HOST, port))
            client_sock.send(length)
            client_sock.sendall(json.dumps(data).encode('utf-8'))
            # client_sock.shutdown(socket.SHUT_WR)
            client_sock.close()
        except:
            print("node " + str(port) + " failed, changing ")
            if port == self.ROOT_PORT:
                self.ROOT_PORT = self.PORT
            self.peers.remove(port)
            self.send_data({'route': 'sync_node_peers','peers': self.peers, 'root_peer': self.ROOT_PORT})
        # self.lock.release()

    def start_server(self):
        self.sock.listen()
        while True:
            # establish connection with client
            conn, addr = self.sock.accept()

            # print('Connected to :', addr[0], ':', addr[1])

            # Start a new thread and return its identifier
            # start_new_thread(handle_clients, (conn, addr))
            self.connections.append(conn)
            thread = threading.Thread(target=self.handle_clients, args=(conn, addr))
            thread.start()
        self.sock.close()

    def handle_clients(self, conn, addr):
        # when sending a file:
        # break the file up into parts each size of a 1000 bytes
        # create a while loop that sends these files to the server while it has not finished sending all the bytes
        # receiving a file:
        #define a string before the loop
        # create a buffer object that receives these buffers and concats them onto the string object
        # print("new client connected ", addr)
        while True:
            bs = conn.recv(4)

            # (length,) = unpack('<L', bs)
            # print(bs.decode())
            try:
                (length,) = unpack('<L', bs)
                # print("recieved len",len(bs))

            except:
                # print(bs, addr)
                # print("for some reason failed")
                break
            # length = int(bs.decode('utf-8'))
            # print("len", length)

            bytes_data = b""
            while len(bytes_data) < length:
                to_read = length - len(bytes_data)

                bytes_data += conn.recv(4096 if to_read > 4096 else to_read)
            # conn.shutdown(socket.SHUT_WR)

            dataJson = bytes_data.decode('utf-8')
            # dataJson = conn.recv(4096).decode('utf-8')
            if not dataJson:
                # print("client disconnected: "+str(addr[1]))
                self.connections.remove(conn)
                break
            print(dataJson)
            data = json.loads(dataJson)
            # print(data)
            # try:
            #
            # except:
            #     print(length, dataJson)
            #     print("exception")

            # .decode('utf-8')
            # if data["route"]=="test":
            #     print("test " + str(self.PORT))

            # add a route where a vm accesses another vm

            ######################
            # with each network request, send the network signature of the client signature. it is used for security between different networking operations between chains

            ######################
            # have a route that is used to set new scripts for routes
            # the request for it includes the route, the route to be added/replaced (cannot contain any of the set routes), the new script and the signature from the client's wallet.
            # this route also checks that the signature provided by the user is the same as the signature stored in the chain
            if data['route'] == 'add_block':
                chain_token = data['chain_token']
                chain = self.chains[chain_token]
                # print(chain.verify_request(data))
                if 'pk_signature' not in data:
                    print(data['route'])
                if chain.verify_request(data):
                    print(data['route'])
                    self.chains[chain_token].add_block(data['block'],data['next_peer'])
            elif data['route'] == 'add_document':
                chain_token = data['chain_token']
                chain = self.chains[chain_token]
                # print(chain.verify_request(data))
                if 'pk_signature' not in data:
                    print(data['route'])
                if chain.verify_request(data):
                    # print(data)
                    self.chains[chain_token].add_document(data['document'])
            elif data['route'] == 'replace_data':
                chain_token = data['chain_token']
                chain = self.chains[chain_token]
                # print(chain.verify_request(data))
                if 'pk_signature' not in data:
                    print(data['route'])
                if chain.verify_request(data):
                    self.chains[chain_token].replace_data(data['chain'], data['pool'], data['peers'], data['next_peer'])
            elif data['route'] == 'sync': #check
                chain_token = data['chain_token']
                chain = self.chains[chain_token]
                # print(chain.verify_request(data))
                if 'pk_signature' not in data:
                    print(data['route'])
                if chain.verify_request(data):
                    new_chain_peers = self.chains[chain_token].sync(data['port'])
                    self.network_chains[chain_token] = new_chain_peers

            elif data['route'] == 'sync_peers': #check
                chain_token = data['chain_token']
                # things to do with peers and connections should all be handled in the node
                # the vm should only know the port, root port and peers
                chain = self.chains[chain_token]
                if 'pk_signature' not in data:
                    print(data['route'])
                if chain.verify_request(data):
                    new_chain_peers = self.chains[chain_token].sync_peers(data['peers'], data['root_peer'])
                    self.network_chains[chain_token] = new_chain_peers
            #####################
            elif data['route'] == 'add_chain':
                # print("add chain")
                chain_token = data['chain_token']
                if self.PORT == data['node_port']:
                    self.add_chain(data['user_pk'], chain_token, data['root_port'], data['eccPrivateKey'], data['skey'])
            elif data['route'] == 'create_chain':
                ct, pk, dd, cn = self.create_chain(2)
                conn.send(
                    json.dumps({'chain_token': ct, 'private_key': pk, 'default_data': dd, 'chain_nodes': cn}).encode(
                        'utf-8'))
            elif data['route'] == 'sync_node':
                self.sync(data['port'])
            elif data['route'] == 'sync_node_peers':
                self.sync_peers(data['peers'], data['root_peer'])
            elif data['route'] == 'sync_network_chains':
                self.network_chains[data["chain_token"]] = data["peers"]
            elif data['route'] == 'upload_script':
                chain_token = data['chain_token']
                self.chains[chain_token].add_script(data)
            elif data['route'] == 'request_access':
                chain_token = data['chain_token']
                accessed_data = self.chains[chain_token].access_data(chain_token, data['access_token'], addr[1])
                conn.send(json.dumps(accessed_data).encode('utf-8'))
            elif data['route'] == 'receive_access':
                chain_token = data['chain_token']
                self.chains[chain_token].receive_access()
            elif data['route'] == 'sync_access_tokens':
                chain_token = data['chain_token']
                chain = self.chains[chain_token]
                if chain.verify_request(data):
                    chain.sync_access_tokens(data['internal_access_tokens'], data['external_access_tokens'])
            else:
                # {'chain_token':'chain_token', 'route':'route', 'content': {}}
                chain_token = data['chain_token']
                chain = self.chains[chain_token]
                print("REACHED")
                if chain.verify_user_request(data):
                    return_data = chain.interact(data)
                    # print(return_data)
                    conn.send(json.dumps(return_data).encode('utf-8'))


        conn.close()


    def start_network(self):
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()
        # for chain in chains: start chain

    def close_server(self):
        self.sock.close()
        print('socket closed')

def print_chain(node, chain_token):
    while True:
        time.sleep(40)
        print(node.chains[chain_token].blockchain_to_json())

def upload_test_data(node, chain_token):
    content = str(secrets.token_hex(16))

    while True:
        time.sleep(30)
        print("testing data upload")
        node.chains[chain_token].interact({'route': 'upload_data', 'data': {'data_token': content},'chain_token': chain_token})
        content = str(secrets.token_hex(16))

def get_test_data(node, chain_token):
    while True:
        time.sleep(20)
        print("testing getting data")
        node.chains[chain_token].interact({'route': 'get_data','chain_token': chain_token})
        time.sleep(20)


def create_test_chain(node, n):
    chain_token, pk, cp, ee = node.create_chain(n)
    # thread = threading.Thread(target=upload_test_data, args=(node, chain_token))
    # thread.start()
    # thread2 = threading.Thread(target=get_test_data, args=(node, chain_token))
    # thread2.start()

if __name__ == '__main__':
    ROOT_PORT = 5000
    # PORT = ROOT_PORT
    # if os.environ['PEER'] == 'TRUE':
    #     PORT = random.randint(5001, 6000)
    # print(socket.gethostbyname(socket.gethostname()))
    node = SocketNode(5000, ROOT_PORT, 'localhost')
    node1 = SocketNode(5001, ROOT_PORT, 'localhost')
    node2 = SocketNode(5002, ROOT_PORT, 'localhost')
    # node3 = SocketNode(5003, ROOT_PORT, 'localhost')
    # node4 = SocketNode(5004, ROOT_PORT, 'localhost')
    # node5 = SocketNode(5005, ROOT_PORT, 'localhost')
    # node6 = SocketNode(5006, ROOT_PORT, 'localhost')
    # time.sleep(30)
    # print(node.peers, node1.peers, node2.peers)
    # create_test_chain(node1, 2)
