import hd_wallet
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
        message1 = []
        entries = []

        word_list = []

        key_selector_first = ''
        key_selector_last = ''

        def __init__(self, salt: str, network: str):
                self.salt = salt
                self.network = network

        def generateSeedFromStr(self, code: str, salt: str):
                seed = pbkdf2.pbkdf2(hashlib.sha512, code, salt, 2048, 64)
                #print('seed = %s' % bytes.decode(binascii.hexlify(seed)))
                return seed

        def on_button(self, y, entry, toplevel):
                #print("%d: %s" % (y, entry.get()))
                self.entries[y] = entry.get()
                if self.entries[y] in self.word_list:
                    self.message1[y].set('%d:correct' % (y+1))
                else:
                    self.message1[y].set('%d:wrong' % (y+1))
                toplevel.destroy()
         
        def callback2(self, test_message):
                #print('entries = %s' % entries)
                joined_word_key_list = ' '.join(self.entries)
                is_valid = mnemonic_code.verifyMnemonicWordCodeString(joined_word_key_list)
                print('is valid = %r' % is_valid)
                if is_valid:
                    test_message.set("Correct")
                else:
                    test_message.set("Wrong")

        def callback(self, y: int):
            toplevel = tkinter.Toplevel()
            message = tkinter.StringVar()
            entry = tkinter.Entry(toplevel, textvariable=message, width=10)
            button = tkinter.Button(toplevel, text="Get", command=lambda y=y, entry=entry, toplevel=toplevel: self.on_button(y, entry, toplevel))
            entry.pack()
            button.pack()

        def on_button_selector(self, e1, e2, root):
                self.key_selector_first = str(e1.get()).replace(' ', '')
                self.key_selector_last = str(e2.get()).replace(' ', '')
                root.destroy()

                if self.key_selector_first[0:2] != 'm/' or self.key_selector_last[0:2] != 'm/' or self.key_selector_first.rsplit('/', 1)[0] != self.key_selector_last.rsplit('/', 1)[0]:
                        print('Invalid selectors')

#def show_entry_fields():
#   print("First Name: %s\nLast Name: %s" % (e1.get(), e2.get()))
#
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

        def get_address_privkey_pair(self, seed_b: bytes):
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
                        #print('child seed = %s' % bytes.decode(binascii.hexlify(b'\x00' + binascii.unhexlify('%064x' % privkey) + binascii.unhexlify('%08x' % index))))
                        #print('h = %s' % bytes.decode(binascii.hexlify(h)))
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
                #print('h[0:32] = %x' % int(binascii.hexlify(h[0:32]), 16))
                #print('privkey = %x' % privkey)
                child_chaincode = h[32:64]
                return childprivkey, child_chaincode

        def generateMasterKeys(self, seed: bytes):
                h = hmac.new(bytes("Bitcoin seed", 'utf-8'),seed, hashlib.sha512).digest()
                private_key = int(binascii.hexlify(h[0:32]), 16)
                chaincode = h[32:64]
                return private_key, chaincode

        def generatePrivkeyPubkeyPair(self, keypath: str, seed: bytes, compressed: bool):
                keypath_list = keypath.replace(' ', '').split('/')
        #        print(keypath_list)
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
                        #print('key = %s' % key)
                        #print('private key = %x, chaincode = %s' % (privkey, bytes.decode(binascii.hexlify(chaincode))))
                privkey_s = '%064x' % privkey
                privkey_b = binascii.unhexlify(privkey_s)
                sk = SigningKey.from_string(privkey_b, curve=SECP256k1)
                vk = sk.get_verifying_key()

                full_pubkey_b = b'\x04' + vk.to_string()
                pubkey = pubkey_address.compressPubkey(full_pubkey_b)
        #        print('privkey = %x, pubkey = %s' % (privkey, bytes.decode(binascii.hexlify(pubkey))))
                return privkey, pubkey

if __name__ == '__main__':
        with open('hd_wallet.conf', 'rt') as wallet_config:
                jsonobj = json.load(wallet_config)
        salt = jsonobj['salt']
        network = jsonobj['network']
        transfer_info_filepath = jsonobj['datadir'] + 'transfer_info.json'

        #salt = 'test'
        #network = 'regtest'

        wallet = HDWallet(salt, network)

        wallet.word_list = mnemonic_code.getMnemonicWordList()

        top = tkinter.Toplevel()
        top.title("RUN ON START TEST")

        testvar = tkinter.StringVar()
        testvar.set("Test")
        get = tkinter.Button(top, textvariable=testvar, command=lambda:wallet.callback2(testvar))

        for y in range(0,12):
                wallet.entries.append('')
                wallet.message1.append(tkinter.StringVar())
                wallet.message1[y].set('%d:unset' % (y+1))
                b = tkinter.Button(textvariable=wallet.message1[y],   command=lambda y=y: wallet.callback(y))
                b.grid(row=0,column=y)
        get.pack()

        top.mainloop()

        mnemonic_code_str = " ".join(wallet.entries)
        print('is valid = %r' % mnemonic_code.verifyMnemonicWordCodeString(mnemonic_code_str))

        seed_b = wallet.generateSeedFromStr(mnemonic_code_str, "mnemonic" + wallet.salt)

        root = tkinter.Tk()
        tkinter.Label(root, text="Access Key First:").grid(row=0)
        tkinter.Label(root, text="Access Key Last").grid(row=1)

        e1 = tkinter.Entry(root)
        e2 = tkinter.Entry(root)

        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)

        tkinter.Button(root, text='Get', command=lambda e1=e1, e2=e2, root=root: wallet.on_button_selector(e1, e2, root)).grid(row=3, column=1, sticky=tkinter.W, pady=4)

        root.mainloop()

        print('1. Generate Addresses')
        print('2. Generate Privkey Address Pair')

        choice = int(input('Selection: '))

        with open(transfer_info_filepath, 'rt') as transfer_info_f:
                jsonobj = json.load(transfer_info_f)

        if choice == 1:
                jsonobj['Addresses'] = wallet.get_addresses(seed_b)
                jsonobj['Address flag'] = 'modified'

                with open('transfer_info.json', 'wt') as transfer_info_f:
                        json.dump(jsonobj, transfer_info_f)

        elif choice == 2:
                address_privkey_map = wallet.get_address_privkey_pair(seed_b)
                privkey_wif_list = []
                for inp in jsonobj['In-use Addresses']['Inputs']:
                        privkey_wif_list.append(address_privkey_map[inp['address']])
 
                jsonobj['Signed Txn'] = sign_raw_txn.return_signed_txn(jsonobj, privkey_wif_list)
                with open('transfer_info.json', 'wt') as transfer_info_f:
                        json.dump(jsonobj, transfer_info_f)
                #print(json.dumps(wallet.get_address_privkey_pair(seed_b)))
        else:
                print('Invalid choice')
