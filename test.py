from pubkey_address import *
import binascii
import cryptos
from ecdsa import SigningKey, SECP256k1
from utility_adapters.hash_utils import hash160


privkey_s = privkeyWif2Hex('Kzvd6SJ7zVXCFYGbZ8tNKfwNDGVFMTQcV9U6uLD3trG9CNxM9NnQ')
print('privkey_s = %s' % privkey_s)

privkey_wif = privkeyHex2Wif(0x6e8f1a5cdbfb6c2d3cbb6d1c29fc8a636c4d59157c502cc70cbb3e008d27092501)
print('******* privkey_wif = %s' % privkey_wif)

pubkey = privkeystr2pubkey(privkey_s)
print('pubkey = %s' % bytes.decode(binascii.hexlify(pubkey)))

hash160_b = hash160(pubkey)
print('hash160 = %s' % bytes.decode(binascii.hexlify(hash160_b)))

script_b = b'\x00\x14' + hash160_b
print('hash160 = %s' % bytes.decode(binascii.hexlify(script_b)))

hash160_script_b = hash160(script_b)
print('hash160 of script = %s' % bytes.decode(binascii.hexlify(hash160_script_b)))

address_s = sh2address(hash160_script_b, "regtest")
print('p2sh-p2wpkh: address = %s' % address_s)
