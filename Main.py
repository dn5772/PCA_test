import pprint
import sys

from AccountModel import AccountModel
from Block import Block
from Blockchain import Blockchain
from Node import Node
from Transaction import Transaction
from TransactionPool import TransactionPool
from Utils import Utils
from Wallet import Wallet


def testCreateTransaction():
    wallet = Wallet()
    
    # create a signed transaction
    receiver = 'receiver'
    amount = 1
    type = 'TRANSFER'
    transaction = wallet.createTransaction(receiver, amount, type)
    print(transaction.toJson())

    # validate transaction's signature
    isSignatureValid = wallet.isSignatureValid(transaction.getPayload(), transaction.signature, wallet.getPubKeyString())
    print(isSignatureValid)

    # create a fraudulent wallet
    fraudulentWallet = Wallet()
    isSignatureValid = wallet.isSignatureValid(transaction.getPayload(), transaction.signature, fraudulentWallet.getPubKeyString())
    print(isSignatureValid)

def testTransactionPool():
    wallet = Wallet()
    transactionPool = TransactionPool()

    transaction = wallet.createTransaction('receiver', 1, 'TRANSFER')
    if transactionPool.transactionExists(transaction) == False:
        transactionPool.addTransaction(transaction)
    print(transactionPool.transactions)

def testCreateBlock():
    wallet = Wallet()
    fraudulentWallet = Wallet()
    # pprint.pprint(blockchain.toJson())
    transactionPool = TransactionPool()
    
    # create a block
    block = wallet.createBlock(transactionPool.transactions, 'lastHash', 1)
    pprint.pprint(block.toJson())

    # validate block's signature
    isBlockSignatureValid = Wallet.isSignatureValid(block.payload(), block.signature, wallet.getPubKeyString())
    print("isBlockSignatureValid", isBlockSignatureValid)
    isBlockSignatureValidWithFraudulentWallet = Wallet.isSignatureValid(block.payload(), block.signature, fraudulentWallet.getPubKeyString())
    print("isBlockSignatureValidWithFraudulentWallet", isBlockSignatureValidWithFraudulentWallet)

def testAddBlockToBlockchain():
    wallet = Wallet()
    blockchain = Blockchain()
    transactionPool = TransactionPool()
    
    # create a block
    lastBlock = blockchain.blocks[-1]
    lastHash = Utils.hash(lastBlock.payload()).hexdigest()
    blockCount = lastBlock.blockCount + 1
    block = wallet.createBlock(transactionPool.transactions, lastHash, blockCount)

    # validate if block is valid
    blockCountValid = blockchain.blockCountValid(block)
    lastBlockHashValid = blockchain.lastBlockHashValid(block)
    print('blockCountValid', blockCountValid)
    print('lastBlockHashValid', lastBlockHashValid)

    # add a block to blockchain
    if blockCountValid and lastBlockHashValid:
        blockchain.addBlock(block)
    pprint.pprint(blockchain.toJson())

def testAccountModel():
    accountModel = AccountModel()
    mine = Wallet()

    accountModel.addAccount(mine.getPubKeyString())
    print('all balances', accountModel.balances)
    print('current account balance', accountModel.getBalance(mine.getPubKeyString()))

    accountModel.updateBalance(mine.getPubKeyString(), 10)
    accountModel.updateBalance(mine.getPubKeyString(), -5)
    print('updated account balance', accountModel.getBalance(mine.getPubKeyString()))

def testAccountModelInBlockchain():
    blockchain = Blockchain()
    pool = TransactionPool()

    alice = Wallet()
    bob = Wallet()
    exchange = Wallet()
    # forger is the one which creates a block
    forger = Wallet()

    # Add 10 tokens to Alice
    exchangeTx = exchange.createTransaction(alice.getPubKeyString(), 10, 'EXCHANGE')
    if not pool.transactionExists(exchangeTx):
        pool.addTransaction(exchangeTx)
    coveredTxs = blockchain.getCoveredTransactions(pool.transactions)
    
    # create first block
    lastBlock = blockchain.blocks[-1]
    lastHash = Utils.hash(lastBlock.payload()).hexdigest()
    blockCount = lastBlock.blockCount + 1
    blockOne = forger.createBlock(coveredTxs, lastHash, blockCount)
    blockchain.addBlock(blockOne)
    pool.removeFromPool(coveredTxs)

    # Alice is sending 5 tokens to Bob
    tx = alice.createTransaction(bob.getPubKeyString(), 5, 'TRANSFER')
    if not pool.transactionExists(tx):
        pool.addTransaction(tx)
    coveredTxs = blockchain.getCoveredTransactions(pool.transactions)

    # create second block
    lastBlock = blockchain.blocks[-1]
    lastHash = Utils.hash(lastBlock.payload()).hexdigest()
    blockCount = lastBlock.blockCount + 1
    blockTwo = forger.createBlock(coveredTxs, lastHash, blockCount)
    blockchain.addBlock(blockTwo)
    pool.removeFromPool(coveredTxs)

    pprint.pprint(blockchain.toJson())

# start a node using `python3 Main.py localhost 10001`
def testP2PNode():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    node = Node(ip, port)

    node.startP2P()
    
def testP2PCommunication():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    node = Node(ip, port)

    node.startP2P()

    # start a node with port 10001 using `python3 Main.py localhost 10001`
    # start a second node with port 10002 using `python3 Main.py localhost 10002`

    # node 2 connects to node 1
    if port == 10002:
        # this block of code is processing inside node 10002
        node.p2p.connect_with_node('localhost', 10001)

def testAPI():
    ip = sys.argv[1]
    p2pPort = int(sys.argv[2])
    apiPort = int(sys.argv[3])
    keyFile = None
    if len(sys.argv) > 4:
        keyFile = sys.argv[4]
    node = Node(ip, p2pPort, keyFile)

    node.startP2P()
    node.startAPI(apiPort)

if __name__ == '__main__':
    # testCreateTransaction()
    # testTransactionPool()
    # testCreateBlock()
    # testAddBlockToBlockchain()
    # testAccountModel()
    # testAccountModelInBlockchain()
    # testP2PNode()
    # testP2PCommunication()
    testAPI()
