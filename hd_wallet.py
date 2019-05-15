import hd_wallet
import pubkey_address
import mnemonic_code
from utility_adapters import hash_utils
from utils import pbkdf2
import tkinter
import json
import binascii
import hashlib

message1 = []
entries = []

word_list = []

g_salt = json.load(open('hd_wallet.conf'))['salt']
g_network = json.load(open('hd_wallet.conf'))['network']

def generateSeedFromStr(code: str, salt: str):
        seed = pbkdf2.pbkdf2(hashlib.sha512, code, salt, 2048, 64)
        #print('seed = %s' % bytes.decode(binascii.hexlify(seed)))
        return seed

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

key_selector_first = ''
key_selector_last = ''
def on_button_selector(e1, e2, root):
        global key_selector_first, key_selector_last

        key_selector_first = str(e1.get()).replace(' ', '')
        key_selector_last = str(e2.get()).replace(' ', '')
        root.destroy()

        if key_selector_first[0:2] != 'm/' or key_selector_last[0:2] != 'm/' or key_selector_first.rsplit('/')[0] == key_selector_last.rsplit('/')[0]:
                print('Invalid selectors')

#def show_entry_fields():
#   print("First Name: %s\nLast Name: %s" % (e1.get(), e2.get()))
#

def get_addresses(seed_b: bytes):
        global key_selector_first, key_selector_last
        addresses = []

        first = int(key_selector_first.rsplit('/', 1)[1])
        last = int(key_selector_last.rsplit('/', 1)[1])

        for index in range(first, last + 1):
                key_selector = '%s/%d' % (key_selector_first.rsplit('/', 1)[0], index)
                print('key_selector = %s' % key_selector)
                privkey_i, chaincode = generatePrivkeyPubkeyPair(key_selector, seed_b, True)
                privkey_wif = pubkey_address.privkey2Wif(privkey_i, g_network)
                pubkey = bytes.decode(binascii.hexlify(chaincode))
                hash160_b = hash_utils.hash160(chaincode)
                script_b = b'\x00\x14' + hash160_b
                hash160_script_b = hash_utils.hash160(script_b)
                addresses.append(pubkey_address.sh2address(hash160_script_b, g_network))

        return addresses

def generate_addresses(mnemonic_code_s: str, first: str, last: str):
        global key_selector_first, key_selector_last
        seed_b = generateSeedFromStr(mnemonic_code_s, "mnemonic" + g_salt)

        key_selector_first = first
        key_selector_last = last

        jsonobj = json.load(open('transfer_info.json', 'rt'))
        jsonobj['addresses'] = get_addresses(seed_b)

        json.dump(jsonobj, open('transfer_info.json', 'wt'))

        return jsonobj

def generateMasterKeys(seed: bytes):
        h = hmac.new(bytes("Bitcoin seed", 'utf-8'),seed, hashlib.sha512).digest()
        private_key = int(binascii.hexlify(h[0:32]), 16)
        chaincode = h[32:64]
        return private_key, chaincode

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
        tkinter.Label(root, text="Access Key First:").grid(row=0)
        tkinter.Label(root, text="Access Key Last").grid(row=1)

        e1 = tkinter.Entry(root)
        e2 = tkinter.Entry(root)

        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)

        tkinter.Button(root, text='Get', command=lambda e1=e1, e2=e2, root=root: on_button_selector(e1, e2, root)).grid(row=3, column=1, sticky=tkinter.W, pady=4)

        root.mainloop()

        jsonobj = json.load(open('transfer_info.json', 'rt'))
        jsonobj['addresses'] = get_addresses(seed_b)

        json.dump(jsonobj, open('transfer_info.json', 'wt'))
