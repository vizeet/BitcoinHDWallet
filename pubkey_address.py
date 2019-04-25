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

def privkey2pubkey(privkey: int):
        bitcoin_sec256k1 = bitcoin_secp256k1.BitcoinSec256k1()
        pubkey = bitcoin_sec256k1.privkey2pubkey(privkey)
#        full_pubkey = b'\x04' + binascii.unhexlify(str('%064x' % pubkey[0])) + binascii.unhexlify(str('%064x' % pubkey[1]))
        full_pubkey = binascii.unhexlify('04%064x%064x' % (pubkey[0],pubkey[1]))
        compressed_pubkey = compressPubkey(full_pubkey)
        return compressed_pubkey

#def privkey2pubkey(privkey: int):
#        order = ecdsa.SECP256k1.generator.order()
#        privkey_b = binascii.unhexlify(str('%064x' % privkey))
#        p = ecdsa.SigningKey.from_string(privkey_b, curve=ecdsa.SECP256k1).verifying_key.pubkey.point
#        x_str = ecdsa.util.number_to_string(p.x(), order)
#        y_str = ecdsa.util.number_to_string(p.y(), order)
#        #pubkey = bitcoin_sec256k1.privkey2pubkey(privkey).to_string()
#        #full_pubkey = b'\x04' + binascii.unhexlify(str('%064x' % x_str)) + binascii.unhexlify(str('%064x' % y_str))
#        full_pubkey = b'\x04' + x_str + y_str
#        compressed_pubkey = compressPubkey(full_pubkey)
#        return compressed_pubkey

def privkeyHex2Wif(privkey: int):
        wif = bitcoin_base58.encodeWifPrivkey(privkey, "mainnet", True)
        return wif

def pkh2address(pkh: bytes):
        address = bitcoin_base58.forAddress(pkh, "mainnet", False)
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
