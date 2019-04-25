import hashlib
import mnemonic_code
import hmac
from utils import pbkdf2
import binascii
import optparse
import sys
from utility_adapters import bitcoin_secp256k1
from utils import base58
import pubkey_address 
import tkinter
from functools import partial 
import pyqrcode
from ecdsa import SigningKey, SECP256k1

message1 = []
entries = []

word_list = []

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

def hash160(secret: bytes):
        secrethash = hashlib.sha256(secret).digest()
        h = hashlib.new('ripemd160')
        h.update(secrethash)
        secret_hash160 = h.digest()
        return secret_hash160

def generateSeedFromStr(code: str, salt: str):
        seed = pbkdf2.pbkdf2(hashlib.sha512, code, salt, 2048, 64)
        #print('seed = %s' % bytes.decode(binascii.hexlify(seed)))
        return seed

def generateMasterKeys(seed: bytes):
        h = hmac.new(bytes("Bitcoin seed", 'utf-8'),seed, hashlib.sha512).digest()
        private_key = int(binascii.hexlify(h[0:32]), 16)
        chaincode = h[32:64]
        return private_key, chaincode

def encodedSerializationKeys(key: int, chaincode: bytes, depth: int, is_private: bool, is_mainnet: bool, child_index=0, parent_key=0):
        if is_private == True:
                if is_mainnet == True:
                        version = b'\x04\x88\xAD\xE4'
                else:
                        version = b'\x04\x35\x83\x94'
        else:
                if is_mainnet == True:
                        version = b'\x04\x88\xB2\x1E'
                else:
                        version = b'\x04\x35\x87\xCF'
        if depth == 0:
                # for root key
                parent_fingerprint = b'\x00\x00\x00\x00'
        else:
                parent_fingerprint = hash160(binascii.unhexlify('%064x' % parent_key))[0:4]

        key_b = b'\x00' + binascii.unhexlify('%064x' % key)
        child_number = binascii.unhexlify('%08x' % child_index)                
        serialized_key = version + bytes([depth]) + parent_fingerprint + child_number + chaincode + key_b
        #print('serialized key = %s' % bytes.decode(binascii.hexlify(serialized_key)))
        h = hashlib.sha256(hashlib.sha256(serialized_key).digest()).digest()
        #print('hash = %s' % bytes.decode(binascii.hexlify(h)))
        serialized_key_with_checksum = int(binascii.hexlify(serialized_key + h[0:4]), 16)
        #print('with checksum: %x' % serialized_key_with_checksum)
        encoded_serialized_key = base58.base58_encode(serialized_key_with_checksum)

        return encoded_serialized_key

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
        print(keypath_list)
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
        parser = optparse.OptionParser(usage="python3 hd_wallet.py -s <Salt>")
        parser.add_option('-s', '--salt', action='store', dest='salt', help='Add salt to secret')
        (args, _) = parser.parse_args()
        if args.salt == None:
                print ("Missing required argument")
                sys.exit(1)

        word_list = mnemonic_code.getMnemonicWordList()

        #top = tkinter.Tk()
        top = tkinter.Toplevel()
        top.title("RUN ON START TEST")
        #frame = tkinter.Frame(top)
        testvar = tkinter.StringVar()
        testvar.set("Test")
        get = tkinter.Button(top, textvariable=testvar, command=lambda:callback2(testvar))
        #get = tkinter.Button(top, text='Get', command=lambda:callback2(testvar))

        for y in range(0,12):
                entries.append('')
                message1.append(tkinter.StringVar())
                message1[y].set('%d:unset' % (y+1))
                #b = tkinter.Button(frame, textvariable=message1[y],   command=lambda y=y: callback(y))
                b = tkinter.Button(textvariable=message1[y],   command=lambda y=y: callback(y))
                b.grid(row=0,column=y)
        #frame.pack()
        get.pack()

        top.mainloop()

        #mnemonic_code_list = mnemonic_code.getMnemonicWordCodeString(12)
        #mnemonic_code = " ".join(mnemonic_code_list)
        mnemonic_code_str = " ".join(entries)
        print('is valid = %r' % mnemonic_code.verifyMnemonicWordCodeString(mnemonic_code_str))
        #print('mnemonic code: %s' % mnemonic_code)
        seed_b = generateSeedFromStr(mnemonic_code_str, "mnemonic" + args.salt)

        master_privkey, master_chaincode = generateMasterKeys(seed_b)

        if master_privkey == 0 or master_privkey >= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F:
                print('invalid master key')

        #print('master private key = %x, master chaincode = %s' % (master_privkey, bytes.decode(binascii.hexlify(master_chaincode))))
        encoded_serialized_key = encodedSerializationKeys(master_privkey, master_chaincode, 0, True, True)
        #print('Encoded Serialized Key = %s' % encoded_serialized_key)

        # for hardened
        child_privkey, child_chaincode = generateChildAtIndex(master_privkey, master_chaincode, 1<<31)
        #print('child private key = %x, child chaincode = %s' % (child_privkey, bytes.decode(binascii.hexlify(child_chaincode))))

        # for normal
        child_privkey, child_chaincode = generateChildAtIndex(master_privkey, master_chaincode, 0)
        #print('child private key = %x, child chaincode = %s' % (child_privkey, bytes.decode(binascii.hexlify(child_chaincode))))

        #print('seed = %s' % bytes.decode(binascii.hexlify(seed_b)))

        #privkey_i, chaincode = generatePrivkeyPubkeyPair('m / 5\'/ 6', seed_b, True)
        #key_selector = 'm/10/2'
        root = tkinter.Tk()
        selector = tkinter.StringVar()
        entry = tkinter.Entry(root, textvariable=selector, width=20)
        button = tkinter.Button(root, text="Get", command=lambda entry=entry, root=root: on_button_selector(entry, root))
        entry.pack()
        button.pack()
        root.mainloop()

        #print('inside main: key_selector = %s' % key_selector)
        privkey_i, chaincode = generatePrivkeyPubkeyPair(key_selector, seed_b, True)
        privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i)
        address_s = pubkey_address.pubkey2address(chaincode)
        #print('keys at m/5\'/6: private key = %s, public key = %s, addess = %s' % (privkey_wif, bytes.decode(binascii.hexlify(chaincode)), address_s))
        print('keys at %s: privkey_i = %x, private key = %s, public key = %s, addess = %s' % (key_selector, privkey_i, privkey_wif, bytes.decode(binascii.hexlify(chaincode)), address_s))


#        root = tkinter.Tk()
#        root.attributes("-fullscreen", True)
#        T = tkinter.Text(root, height=10, width=100, font=("Helvetica", 32))
#        T.pack()
#        T.insert(tkinter.END, address_s)
#        root.mainloop()

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

        if input('address = ') == address_s:
            print('address is valid')
        if input('public key = ') == bytes.decode(binascii.hexlify(chaincode)):
            print('public key is valid')
        if input('private key = ') == privkey_wif:
            print('private key is valid')


#if __name__ == '__main__':
#        mnemonic_code = input
