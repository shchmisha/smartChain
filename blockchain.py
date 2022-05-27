from block import Block

# have a blockchain
# add block
# add new block
# verify chain
# verify doc
# add document to pool
# clear pool
# get valid docs
# to/from json for chain/pool
# replace chain

# for doc pool:
# either change documents to just have data

class Blockchain:
    def __init__(self, default_instructions):
        self.default_instructions = default_instructions
        self.chain = [Block.genesis(default_instructions)]
        self.documentMap = []
        self.length = 0

    def addBlock(self):
        block = Block.mineBlock(self.chain[-1].hash, self.documentMap)
        self.chain.append(block)
        self.length+=1
        return block

    def addNewBlock(self, blockJson):
        block = Block.from_json(blockJson)
        if block.to_json()!=self.chain[-1].to_json():
            if(Block.is_valid_block(self.chain[-1], block)):
                tempChain = self.chain[:]
                tempChain.append(block)
                if Blockchain.isValidChain(tempChain):
                    self.chain.append(block)
                    self.length+=1
                    return True
                else:
                    print('block does not fit')
                    return False
            else:
                print('corrupt block')
                return False
        else:
            print('block already added')
            return True

    def replaceChain(self, chain):
        if len(chain) < len(self.chain):
            # chains can be equal length
            print("chain must be longer")
            return False

        if(not(Blockchain.isValidChain(chain))):
            print('chain not valid')
            return False

        self.chain = chain
        self.length = len(chain)
        return True


    @staticmethod
    def isValidChain(chain):
        # if chain[0].to_json() != Block.genesis().to_json():
        #     print('first block must be genesis')
        #     return False

        for i in range(1, len(chain)):
            block = chain[i]
            last_block = chain[i-1]
            if(not(Block.is_valid_block(last_block, block))):
                print('block '+str(i)+'is not valid')
                return False

        return True

    def blockchain_to_json(self):
        return [block.to_json() for block in self.chain]

    @staticmethod
    def blockchain_from_json(jsonChain):
        return [Block.from_json(blockData) for blockData in jsonChain]




