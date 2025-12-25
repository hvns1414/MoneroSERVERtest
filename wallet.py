from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet

wallet = None

def connect():
    global wallet
    if wallet is None:
        wallet = Wallet(JSONRPCWallet(host="127.0.0.1", port=18082))
    return wallet

def rpc_status():
    try:
        connect().balance()
        return True
    except:
        return False

def balances():
    w = connect()
    return w.balance(), w.unlocked_balance()

def new_address():
    return connect().new_address()

def addresses():
    return list(connect().addresses())

def transfer(addr, amount):
    tx = connect().transfer(addr, amount)
    return tx.hash

def history():
    w = connect()
    h = []
    for tx in w.incoming():
        h.append(("IN", tx.amount, tx.hash))
    for tx in w.outgoing():
        h.append(("OUT", tx.amount, tx.hash))
    return h
