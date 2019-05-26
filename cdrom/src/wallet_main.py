from optparse import OptionParser
import json
import sign_raw_txn
import mnemonic_code
import os
import tkinter

#f_mnemonic_codes = open('mnemonic_code_status.log', 'w+')
#f_hdwallet = open('hdwallet_status.log', 'w+')
#print('key_selector,privkey_wif,pubkey,hash160,script,hash160_script,address', file=f_hdwallet)
#f_hdwallet.flush()
#f_txn = open('txn_status.log', 'w+')
#print('in_privkey_wif,in_address,in_value, out_address, out_value, change_address, change_value, status', file=f_txn)

network_port_map_g = {
        'regtest': 18443,
        'mainnet': 8332
}

transfer_info_map_g = {
        'regtest': 'transfer_info_test.json',
        'mainnet': 'transfer_info.json'
}

# Example mnenomic code
#mnemonic_code_s = "ill virus lottery repair poem injury filter mammal play erase gym camera"

def generate_signed_transaction():
        jsonobj = request.get_json()
        jsonobj = sign_raw_txn.return_signed_txn(jsonobj)
        print('jsonobj = %s' % json.dumps(jsonobj))
        print(jsonobj, file=transfer_info_f)

def generate_address_list(salt: str, network: str):
        import hd_wallet
        global file_path_g

        with open('../../config/hd_wallet.conf', 'rt') as wallet_config:
                jsonobj = json.load(wallet_config)

        wallet = hd_wallet.HDWallet(salt, network)

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

        if os.path.isfile(file_path_g):
                with open(file_path_g, 'rt') as transfer_info_f:
                        jsonobj = json.load(transfer_info_f)
        else:
                jsonobj = {}

        jsonobj['Addresses'] = wallet.get_addresses(seed_b)

        print('jsonobj = %s' % json.dumps(jsonobj))
        with open(file_path_g, 'wt') as transfer_info_f:
                json.dump(jsonobj, transfer_info_f)

if __name__ == '__main__':
        parser = OptionParser()
        parser.add_option("-t", "--test",
                  action="store_true", dest="test",
                  help="Execute in Test Mode")
        (options, _) = parser.parse_args()

        if options.test:
                network = 'regtest'
                datadir = '/tmp/share'
                salt = 'test'
        else:
                with open('../config/hd_wallet.conf', 'rt') as conf_f:
                        jsonobj = json.load(conf_f)
                network = jsonobj['network']
                datadir = jsonobj['datadir']
                salt = jsonobj['salt']

        file_path_g = datadir + os.path.sep + transfer_info_map_g[network]
        port_g = network_port_map_g[network]

        print('1:\tGenerate Addresses')
        print('2:\tSign Transaction')
        choice = int(input('Selection:'))
        if choice == 1:
                generate_address_list(salt, network)
        elif choice == 2:
                generate_signed_transaction()
        else:
                print('Invalid choice')
