from flask import Flask, request, jsonify, make_response, abort
from flask_cors import CORS
import config
import optparse
import socket
import json
import sign_raw_txn
import hd_wallet
import mnemonic_code

app = Flask(__name__)

#f_mnemonic_codes = open('mnemonic_code_status.log', 'w+')
#f_hdwallet = open('hdwallet_status.log', 'w+')
#print('key_selector,privkey_wif,pubkey,hash160,script,hash160_script,address', file=f_hdwallet)
#f_hdwallet.flush()
#f_txn = open('txn_status.log', 'w+')
#print('in_privkey_wif,in_address,in_value, out_address, out_value, change_address, change_value, status', file=f_txn)

@app.route('/addresses', methods=['GET'])
def generate_address_list():
        word_key_list = mnemonic_code.getMnemonicWordCodeString(12)

        mnemonic_code_s = " ".join(word_key_list)

        is_valid = mnemonic_code.verifyMnemonicWordCodeString(mnemonic_code_s)

        print("%s, valid=%r" % (mnemonic_code_s, is_valid), file=f_mnemonic_codes)

        f_mnemonic_codes.flush()

        jsonobj = hd_wallet.generate_addresses(mnemonic_code_s, 'm/2/1', 'm/2/1000')
        abort(make_response(jsonify(json.dumps(jsonobj)), 200))

@app.route('/sign_transaction', methods=['GET'])
def generate_signed_transaction():
        jsonobj = request.get_json()
        jsonobj = sign_raw_txn.return_signed_txn(jsonobj)
        abort(make_response(jsonify(json.dumps(jsonobj)), 200))

if __name__ == '__main__':
        parser = optparse.OptionParser(usage="python3 unittest.py -p <PORT#>")
        parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
        (args, _) = parser.parse_args()
        if args.port == None:
                logging.error ("Missing required argument")
                sys.exit(1)
        app.run(host= socket.gethostname(), port=int(args.port), debug=False, threaded=True)
