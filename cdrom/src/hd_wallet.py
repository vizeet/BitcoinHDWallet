import pubkey_address
import mnemonic_code
from utility_adapters import bitcoin_secp256k1, hash_utils
from utils import pbkdf2
import tkinter
import json
import binascii
import hashlib
import hmac
from ecdsa import SigningKey, SECP256k1
import os
import sign_raw_txn

class HDWallet:
        key_selector_first = ''
        key_selector_last = ''

        def __init__(self, salt: str, network: str):
                self.salt = salt
                self.network = network

        def generateSeedFromStr(self, code: str, salt: str):
                seed = pbkdf2.pbkdf2(hashlib.sha512, code, salt, 2048, 64)
                return seed

        def get_addresses(self, seed_b: bytes):
                addresses = []

                first = int(self.key_selector_first.rsplit('/', 1)[1])
                last = int(self.key_selector_last.rsplit('/', 1)[1])

                for index in range(first, last + 1):
                        key_selector = '%s/%d' % (self.key_selector_first.rsplit('/', 1)[0], index)
                        print('key_selector = %s' % key_selector)
                        print('network = %s' % self.network)
                        privkey_i, chaincode = self.generatePrivkeyPubkeyPair(key_selector, seed_b, True)
                        privkey_wif = pubkey_address.privkey2Wif(privkey_i, self.network)
                        pubkey = bytes.decode(binascii.hexlify(chaincode))
                        hash160_b = hash_utils.hash160(chaincode)
                        script_b = b'\x00\x14' + hash160_b
                        hash160_script_b = hash_utils.hash160(script_b)
                        addresses.append(pubkey_address.sh2address(hash160_script_b, self.network))

                return addresses

        def getAddressPrivkeyMap(self, seed_b: bytes):
                address_privkey_map = {}

                first = int(self.key_selector_first.rsplit('/', 1)[1])
                last = int(self.key_selector_last.rsplit('/', 1)[1])

                for index in range(first, last + 1):
                        key_selector = '%s/%d' % (self.key_selector_first.rsplit('/', 1)[0], index)
                        print('key_selector = %s' % key_selector)
                        print('network = %s' % self.network)
                        privkey_i, chaincode = self.generatePrivkeyPubkeyPair(key_selector, seed_b, True)
                        privkey_wif = pubkey_address.privkey2Wif(privkey_i, self.network)
                        pubkey = bytes.decode(binascii.hexlify(chaincode))
                        hash160_b = hash_utils.hash160(chaincode)
                        script_b = b'\x00\x14' + hash160_b
                        hash160_script_b = hash_utils.hash160(script_b)
                        address = pubkey_address.sh2address(hash160_script_b, self.network)
                        address_privkey_map[address] = privkey_wif

                return address_privkey_map

        def generate_addresses(self, mnemonic_code_s: str, first: str, last: str):
                seed_b = self.generateSeedFromStr(mnemonic_code_s, "mnemonic" + self.salt)

                self.key_selector_first = first
                self.key_selector_last = last

                addresses = self.get_addresses(seed_b)

                return addresses

        def generateChildAtIndex(self, privkey: int, chaincode: bytes, index: int):
                if index >= (1<<31):
                        # hardened
                        #print('hardened')
                        h = hmac.new(chaincode, b'\x00' + binascii.unhexlify('%064x' % privkey) + binascii.unhexlify('%08x' % index), hashlib.sha512).digest()
                else:
                        # normal
                        privkey_s = '%064x' % privkey
                        privkey_b = binascii.unhexlify(privkey_s)
                        sk = SigningKey.from_string(privkey_b, curve=SECP256k1)
                        vk = sk.get_verifying_key()

                        full_pubkey_b = b'\x04' + vk.to_string()
                        pubkey = pubkey_address.compressPubkey(full_pubkey_b)
                        h = hmac.new(chaincode, pubkey + binascii.unhexlify('%08x' % index), hashlib.sha512).digest()
                childprivkey = (int(binascii.hexlify(h[0:32]), 16) + privkey) % bitcoin_secp256k1.N
                child_chaincode = h[32:64]
                return childprivkey, child_chaincode

        def generateMasterKeys(self, seed: bytes):
                h = hmac.new(bytes("Bitcoin seed", 'utf-8'),seed, hashlib.sha512).digest()
                private_key = int(binascii.hexlify(h[0:32]), 16)
                chaincode = h[32:64]
                return private_key, chaincode

        def generatePrivkeyPubkeyPair(self, keypath: str, seed: bytes, compressed: bool):
                keypath_list = keypath.replace(' ', '').split('/')
                if keypath_list[0] != 'm':
                        return None
                for key in keypath_list:
                        if key == 'm':
                                privkey, chaincode = self.generateMasterKeys(seed)
                        else:
                                if "'" in key:
                                        index = int(key[:-1]) + (1<<31)
                                else:
                                        index = int(key)
                                privkey, chaincode = self.generateChildAtIndex(privkey, chaincode, index)
                privkey_s = '%064x' % privkey
                privkey_b = binascii.unhexlify(privkey_s)
                sk = SigningKey.from_string(privkey_b, curve=SECP256k1)
                vk = sk.get_verifying_key()

                full_pubkey_b = b'\x04' + vk.to_string()
                pubkey = pubkey_address.compressPubkey(full_pubkey_b)
                return privkey, pubkey

