from utility_adapters import bitcoin_secp256k1
from utility_adapters import bitcoin_base58
from utility_adapters.bitcoin_secp256k1 import P
import binascii
import hashlib
from utility_adapters import hash_utils
#import ecdsa

# uncompressed public key has b'\x04' prefix
def compressPubkey(pubkey: bytes):
        x_b = pubkey[1:33]
        y_b = pubkey[33:65]
        if (y_b[31] & 0x01) == 0: # even
                compressed_pubkey = b'\x02' + x_b
        else:
                compressed_pubkey = b'\x03' + x_b
        return compressed_pubkey

def privkeystr2pubkey(privkey_s: str):
        compress = False
        if len(privkey_s) == 66:
                privkey_s = privkey_s[0:64]
                compress = True
        privkey_i = int(privkey_s, 16)
        return privkey2pubkey(privkey_i)

def privkey2pubkey(privkey: int):
        bitcoin_sec256k1 = bitcoin_secp256k1.BitcoinSec256k1()
        pubkey = bitcoin_sec256k1.privkey2pubkey(privkey)
#        full_pubkey = b'\x04' + binascii.unhexlify(str('%064x' % pubkey[0])) + binascii.unhexlify(str('%064x' % pubkey[1]))
        full_pubkey = binascii.unhexlify('04%064x%064x' % (pubkey[0],pubkey[1]))
        compressed_pubkey = compressPubkey(full_pubkey)
        return compressed_pubkey

def privkeyHex2Wif(privkey: int, nettype: str):
        wif = bitcoin_base58.encodeWifPrivkey(privkey, nettype, True)
        return wif

def privkeyWif2Hex(privkey: str):
        nettype, prefix, privkey, for_compressed_pubkey = bitcoin_base58.decodeWifPrivkey(privkey)
        return privkey

def pkh2address(pkh: bytes, nettype: str):
        address = bitcoin_base58.forAddress(pkh, nettype, False)
        return address

def sh2address(sh: bytes, nettype: str):
        address = bitcoin_base58.forAddress(sh, nettype, True)
        return address

def pkh2addressLTC(pkh: bytes):
        address = litecoin_base58.forAddress(pkh, "mainnet", False)
        return address

def pubkey2address(pubkey: bytes):
        pkh = hash_utils.hash160(pubkey)
        print('pkh = %s' % bytes.decode(binascii.hexlify(pkh)))
        address = pkh2address(pkh)
        return address

def pubkey2addressLTC(pubkey: bytes):
        pkh = hash_utils.hash160(pubkey)
        print('pkh = %s' % bytes.decode(binascii.hexlify(pkh)))
        address = pkh2addressLTC(pkh)
        return address
