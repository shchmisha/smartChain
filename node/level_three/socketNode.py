import json
import random
import socket
import threading
import time
import secrets

from node.level_two.virtualMachine import Interface
from node.level_two.wallet import Wallet


# add a signalling where a test message is sent out and then if any node responds then they are activeand valid

class SocketNode:
    def __init__(self, PORT, ROOT_PORT, host):
        # each new chain must have a root node for its own sub network
        self.chains = {}
        self.lock = threading.Lock()
        self.connections = []
        self.peers = [ROOT_PORT]
        self.PORT = PORT
        self.ROOT_PORT = ROOT_PORT
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((host, PORT))
        self.start_network()
        if self.PORT != self.ROOT_PORT:
            try:
                client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                client_sock.connect(('localhost', self.ROOT_PORT))
                client_sock.send(json.dumps({'route': 'sync_node','port': self.PORT}).encode('utf-8'))
                client_sock.close()
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
        new_chain = Interface(sign, self.PORT, self.PORT, chain_token, interface_wallet.serializePrivate(), interface_wallet.getSerializedKey())
        self.chains[chain_token] = new_chain

        # introduce thread locks everywhere
        #
        # self.send_data({'chain_token': chain_token, 'route': 'add_chain', 'sign': sign, 'root_port': self.PORT, 'node_port': 5001})
        # self.send_data({'chain_token': chain_token, 'route': 'add_chain', 'sign': sign, 'root_port': self.PORT, 'node_port': 5002})
        #
        # self.send_data({'route': 'add_chain'})
        node = self.peers[random.randint(0, len(self.peers)-1)]
        prev = None
        for i in range(n):
            while True:
                if node == self.PORT or node == prev:
                    node = self.peers[random.randint(0, len(self.peers)-1)]
                else:
                    break
            data = {'chain_token': chain_token, 'route': 'add_chain', 'sign': sign, 'root_port': self.PORT, 'node_port': node, 'eccPrivateKey': interface_wallet.serializePrivate(), 'skey': "skey"}
            self.send_data(data)
            prev = node
            node = self.peers[random.randint(0, len(self.peers)-1)]
        # print(chain_token)
        return chain_token, user_wallet.serializePrivate(), "default_data"




    def add_chain(self, sign, chain_token, root, eccPrivateKey, skey):
        # takes the token, sign and the root port
        # inside the vm, sends a request tothe root node to sync
        if chain_token not in self.chains.keys():
            new_chain = Interface(sign, root, self.PORT, chain_token, eccPrivateKey, skey)
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
                client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    client_sock.connect(('localhost', peer))
                    client_sock.send(json.dumps(data).encode('utf-8'))
                    client_sock.close()
                except:
                    print("node "+str(peer)+" failed, changing ")
                    if peer == self.ROOT_PORT:
                        self.ROOT_PORT = self.PORT
                    self.peers.remove(peer)
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

            dataJson = conn.recv(4096).decode('utf-8')
            # print(dataJson)
            if not dataJson:
                # print("client disconnected: "+str(addr[1]))
                self.connections.remove(conn)
                break
            data = json.loads(dataJson)
            # if data["route"]=="test":
            #     print("test " + str(self.PORT))

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
                    self.chains[chain_token].sync(data['port'])

            elif data['route'] == 'sync_peers': #check
                chain_token = data['chain_token']
                # things to do with peers and connections should all be handled in the node
                # the vm should only know the port, root port and peers
                chain = self.chains[chain_token]
                if 'pk_signature' not in data:
                    print(data['route'])
                if chain.verify_request(data):
                    self.chains[chain_token].sync_peers(data['peers'], data['root_peer'])
            #####################
            elif data['route'] == 'add_chain':
                # print("add chain")
                chain_token = data['chain_token']
                if self.PORT == data['node_port']:
                    self.add_chain(data['sign'], chain_token, data['root_port'], data['eccPrivateKey'], data['skey'])
            elif data['route'] == 'sync_node':
                self.sync(data['port'])
            elif data['route'] == 'sync_node_peers':
                self.sync_peers(data['peers'], data['root_peer'])
            elif data['route'] == 'upload_script':
                chain_token = data['chain_token']
                self.chains[chain_token].add_script(data)
            else:
                # {'chain_token':'chain_token', 'route':'route', 'content': {}}
                chain_token = data['chain_token']
                return_data = self.chains[chain_token].interact(data)
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
        node.chains[chain_token].interact({'route': 'upload_data', 'data': content,'chain_token': chain_token})
        content = str(secrets.token_hex(16))

def get_test_data(node, chain_token):
    while True:
        time.sleep(20)
        print("testing getting data")
        node.chains[chain_token].interact({'route': 'get_data','chain_token': chain_token})
        time.sleep(20)

def create_test_chain(node, n):
    chain_token, pk, cp = node.create_chain(n)
    thread = threading.Thread(target=upload_test_data, args=(node, chain_token))
    thread.start()
    thread2 = threading.Thread(target=get_test_data, args=(node, chain_token))
    thread2.start()

if __name__ == '__main__':
    ROOT_PORT = 5000
    # PORT = ROOT_PORT
    # if os.environ['PEER'] == 'TRUE':
    #     PORT = random.randint(5001, 6000)

    node = SocketNode(5000, ROOT_PORT, 'localhost')
    node1 = SocketNode(5001, ROOT_PORT, 'localhost')
    node2 = SocketNode(5002, ROOT_PORT, 'localhost')
    node3 = SocketNode(5003, ROOT_PORT, 'localhost')
    node4 = SocketNode(5004, ROOT_PORT, 'localhost')
    node5 = SocketNode(5005, ROOT_PORT, 'localhost')
    node6 = SocketNode(5006, ROOT_PORT, 'localhost')
    # time.sleep(30)
    # print(node.peers, node1.peers, node2.peers)
    create_test_chain(node, 4)

# problem arises when the different nodes are mining blocks at the same time







