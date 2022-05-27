from time import time
from node.level_one.cryptoHash import cryptoHash

GENESIS_DATA = {
    'timestamp': 1,
    'lastHash': '-----',
    'data': [],
    'hash': 'hash-one'
}

class Block:
    def __init__(self, timestamp, lastHash, data, hash):
        self.timestamp = timestamp
        self.lastHash = lastHash
        self.data = data
        self.hash = hash

    @staticmethod
    def genesis(default_instructions):
        block_data = GENESIS_DATA
        block_data['data'] = default_instructions
        return Block(**block_data)

    @staticmethod
    def mineBlock(lastHash, data):
        timestamp = time()
        # use merkle tree like structure to store the hash for large files
        # get hash of data like merkle tree from documentmap
        hash = cryptoHash(timestamp, lastHash, data)
        return Block(timestamp, lastHash, data, hash)

    @staticmethod
    def is_valid_block(lastBlock, block):
        if block.lastHash != lastBlock.hash:
            # print(block.lastHash, lastBlock.hash)
            print("hashes dont match")
            return False

        recHash = cryptoHash(block.timestamp, block.lastHash, block.data)
        if block.hash != recHash:
            print("hash is wrong")
            return False

        return True

    def to_json(self):
        return self.__dict__


    @staticmethod
    def from_json(block_json):
        return Block(**block_json)