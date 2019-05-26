from optparse import OptionParser
import json
import sign_raw_txn
import hd_wallet
import mnemonic_code
import os

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

def generate_address_list():
        global file_path_g

        if os.path.isfile(file_path_g):
                with open(file_path_g, 'rt') as transfer_info_f:
                        jsonobj = json.load(transfer_info_f)
        else:
                jsonobj = {}
#        word_key_list = mnemonic_code.getMnemonicWordCodeString(12)
#
#        mnemonic_code_s = " ".join(word_key_list)
#
#        is_valid = mnemonic_code.verifyMnemonicWordCodeString(mnemonic_code_s)

        mnemonic_code_s = "ill virus lottery repair poem injury filter mammal play erase gym camera"

#        print("%s, valid=%r" % (mnemonic_code_s, is_valid), file=f_mnemonic_codes)

#        f_mnemonic_codes.flush()

        wallet = hd_wallet.HDWallet('test', 'regtest')

        jsonobj['Addresses'] = wallet.generate_addresses(mnemonic_code_s, 'm/2/1', 'm/2/30')

        print('jsonobj = %s' % json.dumps(jsonobj))
#        f_mnemonic_codes.close()
        with open(file_path_g, 'wt') as transfer_info_f:
                json.dump(jsonobj, transfer_info_f)

def generate_signed_transaction():
        jsonobj = request.get_json()
        jsonobj = sign_raw_txn.return_signed_txn(jsonobj)
        print('jsonobj = %s' % json.dumps(jsonobj))
        print(jsonobj, file=transfer_info_f)

if __name__ == '__main__':
        network = 'regtest'

        file_path_g = './' + transfer_info_map_g[network]
        port_g = network_port_map_g[network]

        print('1:\tGenerate Addresses')
        print('2:\tSign Transaction')
        choice = int(input('Selection:'))
        if choice == 1:
                generate_address_list()
        elif choice == 2:
                generate_signed_transaction()
        else:
                print('Invalid choice')
