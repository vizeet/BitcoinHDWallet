import mnemonic_code
import os
import random
from utils import pbkdf2
import hashlib
from hd_wallet import *
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
from utility_adapters import hash_utils

salt = json.load(open('hd_wallet.conf'))['salt']

rpc_user = 'test'
rpc_password = 'test'

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:18443"%(rpc_user, rpc_password))

f_mnemonic_codes = open('mnemonic_code_status.log', 'w+')
f_hdwallet = open('hdwallet_status.log', 'w+')
print('key_selector,privkey_wif,pubkey,hash160,script,hash160_script,address', file=f_hdwallet)
f_hdwallet.flush()
f_txn = open('txn_status.log', 'w+')
print('in_privkey_wif,in_address,in_value, out_address, out_value, change_address, change_value, status', file=f_txn)

def get_priv_pub_key():
        word_key_list = mnemonic_code.getMnemonicWordCodeString(12)

        mnemonic_code_str = " ".join(word_key_list)

        is_valid = mnemonic_code.verifyMnemonicWordCodeString(mnemonic_code_str)

        print("%s, valid=%r" % (mnemonic_code_str, is_valid), file=f_mnemonic_codes)

        f_mnemonic_codes.flush()

        seed_b = generateSeedFromStr(mnemonic_code_str, "mnemonic" + salt)

        rnd = random.SystemRandom()

        key_selector_str = 'm/%d/%d/%d' % (rnd.randrange(0x7FFFFFFF), rnd.randrange(0x7FFFFFFF), rnd.randrange(0x7FFFFFFF))

        privkey_i, chaincode = generatePrivkeyPubkeyPair(key_selector_str, seed_b, True)
        privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i, 'regtest')
        pubkey = bytes.decode(binascii.hexlify(chaincode))
        #        address_s = pubkey_address.pubkey2address(chaincode)
        hash160_b = hash_utils.hash160(chaincode)
        script_b = b'\x00\x14' + hash160_b
        hash160_script_b = hash_utils.hash160(script_b)
        address_s = pubkey_address.sh2address(hash160_script_b, "regtest")
#        print('keys at %s: privkey_i = %x, private key = %s, public key = %s, hash160 = %s, p2sh_p2wpkh script = %s, p2sh_p2wsh hash = %s, p2sh_p2wpkh address = %s' % (key_selector_str, privkey_i, privkey_wif, pubkey, bytes.decode(binascii.hexlify(hash160_b)), bytes.decode(binascii.hexlify(script_b)), bytes.decode(binascii.hexlify(hash160_script_b)), address_s))

        print(key_selector_str + ',' + privkey_wif + ',' + pubkey + ',' + bytes.decode(binascii.hexlify(hash160_b)) + ',' + bytes.decode(binascii.hexlify(script_b)) + ',' + bytes.decode(binascii.hexlify(hash160_script_b)) + ',' + address_s, file=f_hdwallet)
        f_hdwallet.flush()
        return privkey_wif, address_s

if __name__ == '__main__':
        while True:
                in_privkey_wif, in_address_s = get_priv_pub_key()

                block_list = rpc_connection.generatetoaddress(1, in_address_s)
        #        print('block_list = %s' % block_list)

                block = rpc_connection.getblock(block_list[0])
                tx_list = block['tx']
                raw_tx = rpc_connection.getrawtransaction(tx_list[0], True)
        #        print('raw_tx = %s' % raw_tx)

                in_value = float(raw_tx['vout'][0]['value'])
        #        print('in_value = %f' % in_value)

                out_value = 1.0

                fee = 0.01

                change_value = in_value - out_value - fee

                out_privkey_wif, out_address_s = get_priv_pub_key()
                change_privkey_wif, change_address_s = get_priv_pub_key()

                tx_in = [{'txid': tx_list[0], "vout": 0}]
                tx_out = [{out_address_s: out_value}, {change_address_s: change_value}]

                new_raw_tx = rpc_connection.createrawtransaction(tx_in, tx_out)

                print('raw transaction = %s' % new_raw_tx)

        #        print('in_privkey_wif = %s, in_address_s = %s' % (in_privkey_wif, in_address_s))

                status = rpc_connection.signrawtransactionwithkey(new_raw_tx, [in_privkey_wif])

                print('status = %s' % status)

                if status['complete'] == True:
                        print('status is complete')
                else:
                        print('status is incomplete')

                print('%s,%s,%f,%s,%f,%s,%f,%r' % (in_privkey_wif, in_address_s, in_value, out_address_s, out_value, change_address_s, change_value, status['complete']), file=f_txn)
                f_txn.flush()

        #        status = rpc_connection.sendrawtransaction(status['hex'])

        #        print('new status = %s' % status)
