import hashlib
import mnemonic_code
import hmac
from utils import pbkdf2
import binascii
import optparse
import sys
from utility_adapters import bitcoin_secp256k1, hash_utils
import pubkey_address 
import tkinter
from functools import partial 
import pyqrcode
from ecdsa import SigningKey, SECP256k1
import json

message1 = []
entries = []

word_list = []

g_salt = json.load(open('hd_wallet.conf'))['salt']
g_network = json.load(open('hd_wallet.conf'))['network']

def on_button(y, entry, toplevel):
        #print("%d: %s" % (y, entry.get()))
        entries[y] = entry.get()
        if entries[y] in word_list:
            message1[y].set('%d:correct' % (y+1))
        else:
            message1[y].set('%d:wrong' % (y+1))
        toplevel.destroy()

def callback2(test_message):
        #print('entries = %s' % entries)
        joined_word_key_list = ' '.join(entries)
        is_valid = mnemonic_code.verifyMnemonicWordCodeString(joined_word_key_list)
        print('is valid = %r' % is_valid)
        if is_valid:
            test_message.set("Correct")
        else:
            test_message.set("Wrong")

def callback(y: int):
    toplevel = tkinter.Toplevel()
    message = tkinter.StringVar()
    entry = tkinter.Entry(toplevel, textvariable=message, width=10)
    button = tkinter.Button(toplevel, text="Get", command=lambda y=y, entry=entry, toplevel=toplevel: on_button(y, entry, toplevel))
    entry.pack()
    button.pack()

key_selector = ''
def on_button_selector(entry, root):
    global key_selector
    key_selector = str(entry.get())
    #print('key_selector = %s' % key_selector)
    root.destroy()


# implementation of BIP32
# mainnet: 0x0488B21E public, 0x0488ADE4 private; testnet: 0x043587CF public, 0x04358394 private

def generateSeedFromStr(code: str, salt: str):
        seed = pbkdf2.pbkdf2(hashlib.sha512, code, salt, 2048, 64)
        #print('seed = %s' % bytes.decode(binascii.hexlify(seed)))
        return seed

def generateMasterKeys(seed: bytes):
        h = hmac.new(bytes("Bitcoin seed", 'utf-8'),seed, hashlib.sha512).digest()
        private_key = int(binascii.hexlify(h[0:32]), 16)
        chaincode = h[32:64]
        return private_key, chaincode

def generateChildAtIndex(privkey: int, chaincode: bytes, index: int):
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

def generatePrivkeyPubkeyPair(keypath: str, seed: bytes, compressed: bool):
        keypath_list = keypath.replace(' ', '').split('/')
#        print(keypath_list)
        if keypath_list[0] != 'm':
                return None
        for key in keypath_list:
                if key == 'm':
                        privkey, chaincode = generateMasterKeys(seed)
                else:
                        if "'" in key:
                                index = int(key[:-1]) + (1<<31)
                        else:
                                index = int(key)
                        privkey, chaincode = generateChildAtIndex(privkey, chaincode, index)
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
        word_list = mnemonic_code.getMnemonicWordList()

        top = tkinter.Toplevel()
        top.title("RUN ON START TEST")

        testvar = tkinter.StringVar()
        testvar.set("Test")
        get = tkinter.Button(top, textvariable=testvar, command=lambda:callback2(testvar))

        for y in range(0,12):
                entries.append('')
                message1.append(tkinter.StringVar())
                message1[y].set('%d:unset' % (y+1))
                b = tkinter.Button(textvariable=message1[y],   command=lambda y=y: callback(y))
                b.grid(row=0,column=y)
        get.pack()

        top.mainloop()

        mnemonic_code_str = " ".join(entries)
        print('is valid = %r' % mnemonic_code.verifyMnemonicWordCodeString(mnemonic_code_str))

        seed_b = generateSeedFromStr(mnemonic_code_str, "mnemonic" + g_salt)

        root = tkinter.Tk()
        selector = tkinter.StringVar()
        entry = tkinter.Entry(root, textvariable=selector, width=20)
        button = tkinter.Button(root, text="Get", command=lambda entry=entry, root=root: on_button_selector(entry, root))
        entry.pack()
        button.pack()
        root.mainloop()

        #print('inside main: key_selector = %s' % key_selector)
        privkey_i, chaincode = generatePrivkeyPubkeyPair(key_selector, seed_b, True)
        privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i, g_network)
        pubkey = bytes.decode(binascii.hexlify(chaincode))
        hash160_b = hash_utils.hash160(chaincode)
        script_b = b'\x00\x14' + hash160_b
        hash160_script_b = hash_utils.hash160(script_b)
        address_s = pubkey_address.sh2address(hash160_script_b, g_network)
        print('keys at %s: privkey_i = %x, private key = %s, public key = %s, hash160 = %s, p2sh_p2wpkh script = %s, p2sh_p2wsh hash = %s, p2sh_p2wpkh address = %s' % (key_selector, privkey_i, privkey_wif, pubkey, bytes.decode(binascii.hexlify(hash160_b)), bytes.decode(binascii.hexlify(script_b)), bytes.decode(binascii.hexlify(hash160_script_b)), address_s))

        code = pyqrcode.create(address_s)
        code_xbm = code.xbm(scale=5)
        top = tkinter.Tk()
        top.attributes("-fullscreen", True)
        code_bmp = tkinter.BitmapImage(data=code_xbm)
        code_bmp.config(foreground="black")
        code_bmp.config(background="white")
        label = tkinter.Label(image=code_bmp)
        label.pack()
        top.mainloop()

#        if input('address = ') == address_s:
#            print('address is valid')
#        if input('public key = ') == bytes.decode(binascii.hexlify(chaincode)):
#            print('public key is valid')
#        if input('private key = ') == privkey_wif:
#            print('private key is valid')


#if __name__ == '__main__':
#        mnemonic_code = input
