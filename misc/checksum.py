from hashlib import sha256

digits58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def decode_base58(bc, length):
	n = 0
	for char in bc:
		n = n * 58 + digits58.index(char)
	return n.to_bytes(length, "big")


def check_bc(bc):
	bcbytes = decode_base58(bc, 25)
	return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]


def validate_address(address):
	# litecoin address' start with L or 3 (for multisig)
	first = {"L", 3}
	if address[0] not in first:
		return False
	# Base58Check
	if not check_bc(address):
		return False
	return True
