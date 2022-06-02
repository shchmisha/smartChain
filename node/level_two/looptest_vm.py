import json
import socket
import random
import threading
import time
from struct import pack

from node.level_one.blockchain import Blockchain
from node.level_two.stringop_tes import Interpreter
from node.level_two.wallet import Wallet

# INTERFACE:
# A parser class which can parse instructions. Will also have the chain tied to it, assigned in the contructor,  to allow blockchain interaction inside the language
# A chain class which holds the chain and the document pool
# the parser class will return it's data that needs to be saved to the blockchain, so that the vm can store in inside the data pool
# REWORK THE DATA POOL TO ACCOUNT FOR DICTIONARIES

# whenever a request is sent to the node, the chain is picked out by it's token. the request is passed onto the interface. once the interface gets the request, it searches through the blockchainfor the latest occurence of an instructionunder the provided name/route
# it then executes that instruction, with the request provided being available to the parser. based on those instructions, and if all the security checks are passed (three sets of private keys' signatures stored in the vm and then checked against the keys provided by the request)
# the instructions can potentially provide an extra level of security, a login system
########## HOW TO MAKE REQUEST DATA ACCESSIBLE TO THE PARSER (maybe the input function?)
# once instructions are executed, and the interractionis complete, the parser returns either data fetchedor a succeess messagefor uploading data
# if data is fetched, the vm formats the data and then sends it as the response

#whenever data is saved or sent to other nodes, it must have the vm's signature


# for every network interaction for each chain, add a signature of the wallet's private key and checkit before each request
# this will add security to the networking functions
#each request must be signed by a wallet

class Interface:
    def __init__(self, sign, root, port, token, eccPrivateKey, skey):
        self.pk_signature = sign
        self.wallet = Wallet(eccPrivateKey, skey)
        self.bc = Blockchain(self.add_default_instructions())
        self.interpreter = Interpreter(self.bc)
        self.root_port = root
        self.port = port
        self.lock = threading.Lock()
        self.next_peer = self.root_port
        self.token = token
        self.peers = [root]
        if self.port != self.root_port:
            try:
                self.send_data_to_port(self.root_port, self.prepare_request({'route': 'sync','port': self.port, 'chain_token': self.token}))
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

    def add_default_instructions(self):
        #     have a route for sending access tokens
        default_instructions = []
        upload_data_script = {'route': "upload_data", 'instruction': "input \"data\" $var upload \"doc_data\" $var"}
        upload_data = {'script': upload_data_script, 'signature': self.wallet.sign(upload_data_script), 'public_key': self.wallet.eccPublicKey}
        default_instructions.append(upload_data)
        get_data_script = {'route': 'get_data', "instruction": "$index = 0 foreach blockchain $var { blockchain return $var \"document\"+$index $index = $index + 1 }"}
        get_data = {'script': get_data_script, 'signature': self.wallet.sign(get_data_script), 'public_key': self.wallet.eccPublicKey}
        default_instructions.append(get_data)
        return default_instructions

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
        if upload_data != {}: # check that the data to upload is not empty
            signature = self.wallet.sign(upload_data)
            data = {'content': upload_data}
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
        if self.pk_signature == request['pk_signature']:
            new_script = {'script':{'route': request['script_route'], 'instruction': request['script']}}
            signature = self.wallet.sign(new_script)
            new_script['signature'] = signature
            new_script['publicKey'] = self.wallet.eccPublicKey
            self.bc.documentMap.append(new_script)
            self.send_data(self.prepare_request({'chain_token': self.token, 'route': 'add_document', 'document': new_script, 'pk_sign': self.pk_signature}))




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
                self.send_data(self.prepare_request({'chain_token': self.token,'route': 'sync_peers','peers': self.peers, 'root_peer': self.root_port, 'pk_sign': self.pk_signature}))
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

        self.send_data_to_port(newPort, self.prepare_request({'chain_token': self.token,'route': 'replace_data', 'chain': self.bc.blockchain_to_json(), 'pool': self.bc.documentMap,'peers': self.peers, 'next_peer': self.next_peer}))
        self.send_data(self.prepare_request({'chain_token': self.token,'route': 'sync_peers','peers': self.peers, 'root_peer': self.root_port}))
        return True

    # network function
    def sync_peers(self,newpeers, root_peer):
        self.peers = newpeers
        self.root_port = root_peer


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
            client_sock.connect(('localhost', port))
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

