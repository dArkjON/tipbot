import json
import subprocess
import sys

# change less than dust gets added to the network fee
dust = 0.0002

def get_new_address(account):
    """
    Returns a new Litecoin address for receiving payments.
    If the given account does not exist it will be created.
    """
    try:
        new_address = subprocess.check_output(["litecoin-cli", "getnewaddress", account])
    except:
        sys.exit(1)

    return new_address.decode().strip()

def dump_priv_key(litecoinaddress):
    """
    Reveals the private key corresponding to litecoinaddress.
    """
    try:
        priv_key = subprocess.check_output(["litecoin-cli", "dumpprivkey", litecoinaddress])
    except:
        sys.exit(1)

    return priv_key.decode().strip()

def list_accounts(min_conf=1):
    """
    Returns a dict that has account names as keys, account balances as values.
    """
    min_conf = str(min_conf)
    try:
        stdout = subprocess.check_output(["litecoin-cli", "listaccounts", min_conf])
        accounts = json.loads(stdout.decode())
    except:
        sys.exit(1)

    return accounts

def get_addresses_by_account(account):
    """
    Returns a list of addresses for the given account.
    """
    try:
        stdout = subprocess.check_output(["litecoin-cli", "getaddressesbyaccount", account])
        addresses = json.loads(stdout.decode())
    except:
        sys.exit(1)

    return addresses

def list_unspent(litecoinaddress, min_conf=1, max_conf=99999999):
    """
    Returns a list of unspent transaction inputs in the wallet
    """
    min_conf = str(min_conf)
    max_conf = str(max_conf)
    a = [litecoinaddress]
    try:
        stdout = subprocess.check_output(["litecoin-cli", "listunspent", min_conf, max_conf, json.dumps(a)])
        unspent = json.loads(stdout.decode())
    except:
        sys.exit(1)
        
    return unspent

def get_address_balance(litecoinaddress):
    """
    Returns the balance for litecoinaddress
    """
    total_balance = 0
    unspent = list_unspent(litecoinaddress)
    for block in unspent:
        total_balance += float(block["amount"])

    return total_balance

def get_account_balance(account):
    """
    Returns the balance in the account.
    """
    balance = 0

    for address in get_addresses_by_account(account):
        balance += get_address_balance(address)

    return float(balance)

def create_raw_transaction(amount, network_fee, from_address, to_address):
    """
    Creates a raw transaction spending given inputs.
    Returns transaction hexstring.
    """
    tx_total = amount + network_fee
    tx_inputs = []
    input_total = 0
    unspent = list_unspent(from_address)

    # Are there enough funds in one block to cover the amount
    for block in unspent:
        if float(block["amount"]) >= tx_total:
            tx_input = {"txid": block["txid"], "vout": int(block["vout"])}
            input_total = float(block["amount"])
            tx_inputs.append(tx_input)
            break
    # If tx_inputs is empty that means we have to
    # build the transaction from multiple blocks
    if not tx_inputs:
        for block in unspent:
            if input_total >= tx_total:
                break
            else:
                tx_input = {"txid": block["txid"], "vout": int(block["vout"])}
                input_total += float(block["amount"])
                tx_inputs.append(tx_input)

    # Amount left over after amount to send and network fees are subtracted
    # from input_total. Change is sent back to sender
    change = round((input_total - amount) - network_fee, 8)
    
    if change < dust:
        tx_output = {to_address: amount}
    else:
        tx_output = {to_address: amount, from_address: change}
    
    try:
        tx_hex_string = subprocess.check_output(["litecoin-cli", "createrawtransaction", json.dumps(tx_inputs), json.dumps(tx_output)])
    except:
        sys.exit(1)

    return tx_hex_string.strip()

def sign_raw_transaction(hexstring):
    """
    Adds signatures to a raw transaction and returns the resulting raw transaction.
    """
    try:
        stdout = subprocess.check_output(["litecoin-cli", "signrawtransaction", hexstring])
        signed_tx = json.loads(stdout.decode())
    except:
        sys.exit(1)

    return signed_tx 

def send_raw_transaction(signed_tx):
    """
    RPC validates a transaction and broadcasts it to the peer-to-peer network.
    returns a transaction hash (txid) as it submits the transaction on the network.
    """
    try:
        txid = subprocess.check_output(["litecoin-cli", "sendrawtransaction", signed_tx])
    except:
        sys.exit(1)
    return txid.strip()

def withdraw_from_address(amount, network_fee, from_address, to_address):
    """
    Withdraws ammount from 'from_address' and sends it to 'to_address'
    Returns the transaction ID if successful
    """
    tx_total = amount + network_fee
    address_balance = get_address_balance(from_address)

    if tx_total > address_balance:
        # return not enough funds error
        print("Error: Not enough funds")
    else:
        tx_hex_string = create_raw_transaction(amount, network_fee, from_address, to_address)
        signed_tx = sign_raw_transaction(tx_hex_string)
        hex_signed_tx =  signed_tx["hex"]
        txid = send_raw_transaction(hex_signed_tx)

        return txid.decode()

def withdraw_from_account(amount, from_account, to_address, min_conf=1):
    """ 
    Will send amount from 'from_account' to 'to_address', 
    ensuring the account has a valid balance using minconf 
    confirmations. Returns the transaction ID if successful
    """
    amount = str(amount)
    min_conf = str(min_conf)
    
    try:
        txid = subprocess.check_output(["litecoin-cli", "sendfrom", from_account, to_address, amount, min_conf])
    except:
        sys.exit(1)

    return txid.decode().strip()