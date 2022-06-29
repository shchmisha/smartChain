import json
import secrets
import socket
import random
import threading
import time
from struct import pack

from node.level_one.blockchain import Blockchain
from node.level_two.stringop_tes import Interpreter
from node.level_two.wallet import Wallet


# how to add data access tokens in
# have a data access token dictionary
# tokens act as keys for the index of the document
# when accessed, token is removed, the interaction is recorded, and data at that index is sent to the client
# when granting, token is created, assigned a document and sent to the node that requests the token

# main questions:
#   how does the interpereter communicate with the sn
# when a script requesting data access is run, it connects to the vm that hold the

# data access tokens:
# stored in each vm
# internal data access tokens are stored in a dictionary, where the key is the token and the value is the name of the document/index of doc/directory and name
# external data access tokens are stored in a dictionary, where the key is the token and the value is the port
# when accessing data access tokens, the request must include the token and the chain token of both vms
# when recieving the request, must check the chain token, the access token and the port of the vm

# grant access: adds data token and sends to vm


class Interface:
    def __init__(self, user_pk, root, port, token, eccPrivateKey, skey, host, node):
        self.user_pk = user_pk
        self.node = node
        self.wallet = Wallet(eccPrivateKey, skey)
        self.bc = Blockchain(self.add_default_instructions())
        self.interpreter = Interpreter(self.bc, self)
        self.root_port = root
        self.port = port
        self.host = host
        self.lock = threading.Lock()
        self.next_peer = self.root_port
        self.token = token
        self.peers = [root]
        self.internal_access_tokens = {}
        self.external_access_tokens = {}
        if self.port != self.root_port:
            try:
                self.send_data_to_port(self.root_port, self.prepare_request(
                    {'route': 'sync', 'port': self.port, 'chain_token': self.token}))
            except:
                print("error syncing chain")
        thread = threading.Thread(target=self.mine_blocks)
        thread.start()
        print(str(self.port))

    def prepare_request(self, data):
        signature = self.wallet.sign(data)
        data['pk_signature'] = signature
        return data

    def verify_request(self, request):
        signature = request['pk_signature']
        request.pop('pk_signature')
        return self.wallet.verify(self.wallet.eccPublicKey, request, signature)

    def verify_user_request(self, request):
        signature = request['pk_signature']
        request.pop('pk_signature')
        return self.wallet.verify(self.user_pk, request, signature)

    def add_default_instructions(self):
        #     have a route for sending access tokens
        default_instructions = []
        upload_data_script = {'route': "upload_data", 'instruction': "input \"data\" $var upload \"doc_data\" $var"}
        upload_data = {'script': upload_data_script, 'signature': self.wallet.sign(upload_data_script),
                       'public_key': self.wallet.eccPublicKey}
        default_instructions.append(upload_data)
        get_data_script = {'route': 'get_data',
                           "instruction": " $arr = [ ] foreach blockchain $var { $arr append $var } blockchain return $arr \"data\" "}
        get_data = {'script': get_data_script, 'signature': self.wallet.sign(get_data_script),
                    'public_key': self.wallet.eccPublicKey}
        default_instructions.append(get_data)

        get_named_doc_script = {'route': "get_named_data",
                                'instruction': " input \"doc_name\" $name blockchain get $var $name blockchain return $var \"data\" "}
        get_named_doc = {'script': get_named_doc_script, 'signature': self.wallet.sign(get_named_doc_script),
                         'public_key': self.wallet.eccPublicKey}
        default_instructions.append(get_named_doc)
        return default_instructions

    def get_doc_index_by_name(self, doc_name):

        # idea:
        # iteerate through the blockchain backwards
        # the first occurance that arises is the index at which

        block_index = len(self.bc.chain) - 1
        data_index = 0
        while block_index >= 0:
            data_index = len(self.bc.chain[block_index].data) - 1
            block = self.bc.chain[block_index]
            while data_index >= 0:
                if "content" in block.data[data_index] and "name" in block.data[data_index]["content"]:
                    if doc_name == block.data[data_index]["content"]["name"]:
                        break
                data_index -= 1
            block_index -= 1
        return (block_index, data_index)

    def get_doc_by_index(self, block_index, data_index):
        i = 0
        j = 0
        fetched_data = None
        while i < block_index:
            while j < data_index:
                fetched_data = self.bc.chain[i].data[j]
                j += 1
            i += 1
        return fetched_data

    def get_doc_by_name(self, doc_name):
        fetched_data = None
        for block in self.bc.chain:
            for data in block.data:
                # print(self.lex(json.dumps(data)))
                if "content" in data and "name" in data["content"]:
                    if doc_name == data["content"]["name"]:
                        fetched_data = data["content"]
        return fetched_data

    def grant_access(self, chain_token, name_of_doc):
        access_token = secrets.token_hex(16)
        data_index = self.get_doc_index_by_name(name_of_doc)
        port = self.node.network_chains[chain_token][random.randint(0, len(self.node.network_chains[chain_token]))]
        self.internal_access_tokens[access_token] = {'data_index': data_index, 'chain_token': chain_token}
        # sync access tokens accross vm
        self.send_data_to_port(port, {'chain_token': chain_token, 'route': 'receive_access',
                                      'external_chain_token': self.token, 'access_token': access_token})
        self.send_data({'chain_token': self.token, 'route': 'sync_access_tokens',
                        'internal_access_tokens': self.internal_access_tokens,
                        'external_access_tokens': self.external_access_tokens})

    def receive_access(self, data_access_token, chain_token):
        self.external_access_tokens[data_access_token] = chain_token
        self.send_data({'chain_token': self.token, 'route': 'sync_access_tokens',
                        'internal_access_tokens': self.internal_access_tokens,
                        'external_access_tokens': self.external_access_tokens})

    def request_access(self, access_token):
        if access_token in self.external_access_tokens:
            chain_token = self.external_access_tokens[access_token]
            port = self.node.network_chains[chain_token][random.randint(0, len(self.node.network_chains[chain_token]))]
            data = {"chain_token": chain_token, "route": "request_access", "access_token": access_token}
            # make sure the connecton can receive data
            length = pack('<L', len(json.dumps(data).encode('utf-8')))
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_sock.connect((self.host, port))
                client_sock.send(length)
                client_sock.sendall(json.dumps(data).encode('utf-8'))
                recv_data = client_sock.recv(4096)
                dataJson = recv_data.decode('utf-8')
                dec_data = json.loads(dataJson)
                del self.internal_access_tokens[access_token]
                return dec_data
            except:
                if port == self.root_port:
                    self.root_port = self.port
                self.peers.remove(port)
                self.send_data(self.prepare_request(
                    {'chain_token': self.token, 'route': 'sync_peers', 'peers': self.peers,
                     'root_peer': self.root_port}))
        return None

    def data_access(self, access_token, port):
        if access_token in self.internal_access_tokens:
            token_data = self.internal_access_tokens[access_token]
            if port in self.node.network_chains[token_data['chain_token']]:
                data = self.get_doc_by_index(token_data['index'][0], token_data['index'][1])
                del self.internal_access_tokens[access_token]
                return data
        return None

    def sync_access_tokens(self, internal_access_tokens, external_access_tokens):
        self.internal_access_tokens = internal_access_tokens
        self.external_access_tokens = external_access_tokens

        # network function

    def replace_data(self, chain, pool, peers, next_peer):
        self.peers = peers
        self.next_peer = next_peer
        newChain = self.bc.blockchain_from_json(chain)
        self.bc.documentMap = pool
        # if the chain length is one and it only holds is the initial instructions,
        replaced = self.bc.replaceChain(newChain)
        return replaced

    # network function
    def blockchain_mine(self):
        if self.port == self.next_peer:
            block = self.bc.addBlock()
            # self.bc.clearBlockchainDocuments()
            # print(self.bc.blockchain_to_json())
            print(self.port)
            # print(self.bc.blockchain_to_json())
            self.bc.documentMap = []
            next_peer = self.peers[random.randint(0, len(self.peers) - 1)]
            # print("actual next peer", next_peer, self.peers)
            self.next_peer = next_peer

            self.send_data(self.prepare_request(
                {'chain_token': self.token, 'route': 'add_block', 'block': block.to_json(),
                 'next_peer': self.next_peer}))

            return block.to_json()

    # add way to send data access tokens to other chains and get access to data from other networks
    # either:
    #   have a separate route, where a chain token is provided in the request. the token is generated, stored in the interface and sent around the network to reach the correct chain
    # or:
    #   create a way to make tokens in chainScript. create another BLOCKCHAIN function, which is used to send the token around to other chains

    def interact(self, user_request):
        # what to do:
        # figure out what needs to be inside each request, document and script and how to store them

        # search for an instruction with the route of uploading a doc
        instruction = ""
        for block in self.bc.chain:
            for data in block.data:

                # print(data)
                if "script" in data:
                    if data["script"]["route"] == user_request["route"]:
                        instruction = data["script"]["instruction"]

        # print(instruction)
        self.interpreter.user_request = user_request
        # print(self.interpreter.user_request)
        upload_data, return_data = self.interpreter.exec_instruction_test(instruction)
        print(upload_data, return_data)
        if upload_data != {}:  # check that the data to upload is not empty
            # signature = self.wallet.sign(upload_data)
            signature = self.wallet.sign(upload_data['doc_data'])
            # data = {'content': upload_data}
            data = {'content': upload_data['doc_data']}
            data["signature"] = signature
            data["public_key"] = self.wallet.eccPublicKey
            self.bc.documentMap.append(data)
            self.send_data(self.prepare_request({'chain_token': self.token, 'route': 'add_document', 'document': data}))
        # print(self.bc.blockchain_to_json())
        # here the blockchain will record the interaction in the chain
        # it will consist of the timestamp, the signature from the interface
        return return_data

    def add_script(self, request):
        # {'chain_token': 'chain_token', 'route': 'add_script', 'script': 'script', 'script_route': 'script_route', 'pk_signature': 'pk_signature'}
        if self.verify_user_request(request):
            new_script = {'script': {'route': request['script_route'], 'instruction': request['script']}}
            signature = self.wallet.sign(new_script)
            new_script['signature'] = signature
            new_script['publicKey'] = self.wallet.eccPublicKey
            self.bc.documentMap.append(new_script)
            self.send_data(
                self.prepare_request({'chain_token': self.token, 'route': 'add_document', 'document': new_script}))




    def add_document(self,data):
        if self.wallet.verify(data['public_key'], data['content'], data['signature']):
            self.bc.documentMap.append(data)
        else:
            print("Doc check failed")
            pass
    #          for each request, we want to get a response
    #          response can be something to

    # network function
    def add_block(self, blockJson, next_peer):
        # need to make sure that next_peer is assigned at the correct time
        self.next_peer = next_peer
        if(self.bc.addNewBlock(blockJson)):
            print("valid block")
            self.bc.documentMap = []
            # self.bc.clearBlockchainDocuments()
            return True
        #     think about how the data will be passed on
        else:
            # instead of just syncing, try to either sync or a signal is set to node sending the block that the block is wrong
            # the two nodes need to work out who is wrong, either by consensus or by checking each other's chains against each other
            peer = self.peers[random.randint(0, len(self.peers)-1)]
            try:
                self.send_data_to_port(peer, self.prepare_request({'chain_token': self.token,'route': 'replace_data', 'chain': self.bc.blockchain_to_json(), 'pool': self.bc.documentMap,'peers': self.peers, 'next_peer': self.next_peer}))
            except:
                if peer == self.root_port:
                    self.root_port = self.port
                self.peers.remove(peer)
                self.send_data(self.prepare_request(
                    {'chain_token': self.token, 'route': 'sync_peers', 'peers': self.peers,
                     'root_peer': self.root_port}))
            # send request to replace the chain
            return False

    #network function
    def sync(self,newPort):
        # syncing in the chain:
        # each chain has it's own root port and port to determine who mines next and who to sync wwith
        # this means that syncing has to be done individually
        if newPort not in self.peers:
            self.peers.append(newPort)
        # print(newPort)

        self.send_data_to_port(newPort, self.prepare_request(
            {'chain_token': self.token, 'route': 'replace_data', 'chain': self.bc.blockchain_to_json(),
             'pool': self.bc.documentMap, 'peers': self.peers, 'next_peer': self.next_peer}))
        self.send_data(self.prepare_request(
            {'chain_token': self.token, 'route': 'sync_peers', 'peers': self.peers, 'root_peer': self.root_port}))
        self.node.send_data({"route": "sync_network_chains", "chain_token": self.token, "peers": self.peers})
        return self.peers

    # network function
    def sync_peers(self,newpeers, root_peer):
        self.peers = newpeers
        self.root_port = root_peer
        return self.peers


    # network function
    def send_data(self, data):
        # self.lock.acquire()
        for peer in self.peers:
            if peer != self.port:
                self.send_data_to_port(peer, data)
        # self.lock.release()


    def send_data_to_port(self, port, data):
        length = pack('<L', len(json.dumps(data).encode('utf-8')))
        # length = str(len(json.dumps(data).encode('utf-8'))).encode('utf-8')
        # self.lock.acquire()
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_sock.connect((self.host, port))
            client_sock.send(length)
            client_sock.sendall(json.dumps(data).encode('utf-8'))
            # client_sock.shutdown(socket.SHUT_WR)
            client_sock.close()
        except:
            if port == self.root_port:
                self.root_port = self.port
            self.peers.remove(port)
            self.send_data(self.prepare_request({'chain_token': self.token, 'route': 'sync_peers','peers': self.peers, 'root_peer': self.root_port}))
        # self.lock.release()

    def mine_blocks(self):
        count = 0
        while True:
            time.sleep(10.0)
            # print(self.bc.doc_map_to_json())
            self.blockchain_mine()
            #     count+=1
            # self.blockchain_mine()
            # print(self.next_peer, self.port, count)
            time.sleep(10.0)

