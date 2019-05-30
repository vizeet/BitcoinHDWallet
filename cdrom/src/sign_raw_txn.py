# This file is just for the time parser library is not ready

import json
import mmap
import binascii
from utility_adapters import hash_utils
import pubkey_address
import ecdsa

#"Input txn": [{"value": 50.00000000, "scriptPubKey": "a9143dac417e755b3445891111b96aad23626ecfe49587"}],
#        "Raw txn": "0200000001aecf5c19f7d9c1cb83d193df7b5f351ef6636b68a62280d07d12c9a73b3554a70000000000ffffffff0200f902950000000017a9142aa793f2e0d059d12fbe77edd743eb341559f0f187c0ebff940000000017a91436f2c696e6f4f335d35d27aa537446194e8394638700000000"

def btc2bytes(btc: float):
        satoshis = int(btc * (10**8))
        print('satoshis = %s' % satoshis)
        satoshis_s = '%016x' % satoshis

        if satoshis_s.__len__() % 2 == 1:
                satoshis_s = "0{}".format(satoshis_s)

        hex_b = binascii.unhexlify(satoshis_s)[::-1]
        return hex_b

def bytes2btc(hex_b: bytes):

        satoshis = int(binascii.hexlify(hex_b[::-1]), 16)
        btc = satoshis/ (10 ** 8)
        
        return btc

def getCount(count_bytes):
        txn_size = int(binascii.hexlify(count_bytes[0:1]), 16)

        if txn_size < 0xfd:
                return txn_size
        elif txn_size == 0xfd:
                txn_size = int(binascii.hexlify(count_bytes[1:3][::-1]), 16)
                return txn_size
        elif txn_size == 0xfe:
                txn_size = int(binascii.hexlify(count_bytes[1:5][::-1]), 16)
                return txn_size
        else:
                txn_size = int(binascii.hexlify(count_bytes[1:9][::-1]), 16)
                return txn_size

def getCountBytes(mptr: mmap):
        mptr_read = mptr.read(1)
        count_bytes = mptr_read
        txn_size = int(binascii.hexlify(mptr_read), 16)

        if txn_size < 0xfd:
                return count_bytes
        elif txn_size == 0xfd:
                mptr_read = mptr.read(2)
                count_bytes += mptr_read
                txn_size = int(binascii.hexlify(mptr_read[::-1]), 16)
                return count_bytes
        elif txn_size == 0xfe:
                mptr_read = mptr.read(4)
                count_bytes += mptr_read
                txn_size = int(binascii.hexlify(mptr_read[::-1]), 16)
                return count_bytes
        else:
                mptr_read = mptr.read(8)
                count_bytes += mptr_read
                txn_size = int(binascii.hexlify(mptr_read[::-1]), 16)
                return count_bytes

def getTxnReqIndexesForSigning(mptr: mmap):
        prev1_ptr = mptr.tell()
        mptr.seek(0)
        prev_ptr = 0

        sign_helper = {}
        mptr.read(4) # version

        ptr = mptr.tell()
        sign_helper['segwit_marker'] = {}
        sign_helper['segwit_marker']['loc'] = ptr - prev_ptr
        prev_ptr = ptr

        mptr_read = getCountBytes(mptr) # input count bytes

        # input count
        input_count = getCount(mptr_read)

        sign_helper['signatures'] = []
        # inputs
        for index in range(input_count):
                signature = {}
                mptr.read(32 + 4) # input txn hash + input out index

                ptr = mptr.tell()
                signature['loc'] = ptr - prev_ptr

                mptr_read = mptr.read(1) # scriptsig size bytes which is 0
                prev_ptr = ptr + 1
                mptr.read(4) # sequence
                sign_helper['signatures'].append(signature)

        mptr_read = getCountBytes(mptr) # out count bytes

        out_count = getCount(mptr_read) # out count

        # outs
        for index in range(out_count):
                mptr.read(8) # value
                mptr_read = getCountBytes(mptr) # scriptpubkey size bytes
                scriptpubkey_size = getCount(mptr_read)
                mptr_read = mptr.read(scriptpubkey_size) # scriptpubkey

        ptr = mptr.tell()
        sign_helper['segwit'] = {}
        sign_helper['segwit']['loc'] = ptr - prev_ptr
        prev_ptr = ptr

        mptr.seek(prev1_ptr)

        return sign_helper

def getInputCountFromTxn(mptr: mmap):
        prev_ptr = mptr.tell()
        mptr.seek(0)
        mptr.read(4)
        mptr_read = getCountBytes(mptr)
        input_count = getCount(mptr_read)
        if input_count == 0:
                is_segwit = int(binascii.hexlify(mptr.read(1)), 16)
                if is_segwit == 0x01:
                        mptr_read = getCountBytes(mptr)
                        input_count = getCount(mptr_read)
        mptr.seek(prev_ptr)

        return input_count

def getSizeRawTxn(mptr: mmap):
        prev_ptr = mptr.tell()
        mptr.seek(0)
        mptr.read(4) # version
        mptr_read = getCountBytes(mptr) # input count bytes

        # input count
        input_count = getCount(mptr_read)

        # inputs
        for index in range(input_count):
                mptr.read(32 + 4) # input txn hash + input out index
                mptr_read = getCountBytes(mptr) # scriptsig size bytes
                scriptsig_size = getCount(mptr_read)
                mptr.read(scriptsig_size) # scriptsig
                mptr.read(4) # sequence

        mptr_read = getCountBytes(mptr) # out count bytes

        out_count = getCount(mptr_read) # out count

        # outs
        for index in range(out_count):
                mptr.read(8) # value
                mptr_read = getCountBytes(mptr) # scriptpubkey size bytes
                scriptpubkey_size = getCount(mptr_read)
                mptr_read = mptr.read(scriptpubkey_size) # scriptpubkey
        mptr_read = mptr.read(4) # locktime

        raw_txn_size = mptr.tell()
        mptr.seek(prev_ptr)

        return raw_txn_size

def estimateSignedTxnSize(mptr: mmap, txn_type = "p2sh-p2wpkh"):
        input_count = getInputCountFromTxn(mptr)

        witness_flag_size = 2
        signature_size = input_count * 0x18
        witness_size = input_count * 0x4a + 1

        raw_txn_size = getSizeRawTxn(mptr)

        estimated_signed_txn_size = witness_flag_size + signature_size + witness_size + raw_txn_size

        return estimated_signed_txn_size

def validateRawTxn(mptr: mmap):
        pass

def sign_txn_input(preimage: bytes, privkey_wif: str):
        hash_preimage = hash_utils.hash256(preimage)
        privkey_s = pubkey_address.privkeyWif2Hex(privkey_wif)
        privkey_b = binascii.unhexlify(privkey_s)[:-1]
        signingkey = ecdsa.SigningKey.from_string(privkey_b, curve=ecdsa.SECP256k1)
        sig_b = signingkey.sign_digest(hash_preimage, sigencode=ecdsa.util.sigencode_der_canonize) +b'\x01'
        return sig_b

def get_p2sh_witness_redeem_script(hash_b: bytes):
        size = len(hash_b)
        script_b = bytes([0, size]) + hash_b
        return script_b

def get_preimage_hashes(mptr: mmap):
        prev_ptr = mptr.tell()
        prevouts = b''
        out_txn = b''
        outpoints = []
        sequences = []
        mptr.seek(0)
        mptr.read(4) # version
        mptr_read = getCountBytes(mptr) # input count bytes

        # input count
        input_count = getCount(mptr_read)

        # inputs
        for index in range(input_count):
                mptr_read = mptr.read(32 + 4) # input txn hash + input out index
                outpoints.append(mptr_read)
                prevouts += mptr_read
                mptr.read(1) # scriptsig size bytes which is 0
                sequences.append(mptr.read(4))

        mptr_read = getCountBytes(mptr) # out count bytes

        out_count = getCount(mptr_read) # out count

        # outs
        for index in range(out_count):
                mptr_read = mptr.read(8) # value
                out_txn += mptr_read
                mptr_read = getCountBytes(mptr) # scriptpubkey size bytes
                out_txn += mptr_read
                scriptpubkey_size = getCount(mptr_read)
                out_txn += mptr.read(scriptpubkey_size) # scriptpubkey
        print('out_txn = %s' % bytes.decode(binascii.hexlify(out_txn)))
        locktime_b = mptr.read(4)
        mptr.seek(prev_ptr)

        hash_prevouts = hash_utils.hash256(prevouts)
        hash_sequence = hash_utils.hash256(b''.join(sequences))
        hash_outs = hash_utils.hash256(out_txn)

        return hash_prevouts, hash_sequence, outpoints, sequences, hash_outs, locktime_b

#    nVersion:     01000000
#    hashPrevouts: b0287b4a252ac05af83d2dcef00ba313af78a3e9c329afa216eb3aa2a7b4613a
#    hashSequence: 18606b350cd8bf565266bc352f0caddcf01e8fa789dd8a15386327cf8cabe198
#    outpoint:     db6b1b20aa0fd7b23880be2ecbd4a98130974cf4748fb66092ac4d3ceb1a547701000000
#    scriptCode:   1976a91479091972186c449eb1ded22b78e40d009bdf008988ac
#    amount:       00ca9a3b00000000
#    nSequence:    feffffff
#    hashOutputs:  de984f44532e2173ca0d64314fcefe6d30da6f8cf27bafa706da61df8a226c83
#    nLockTime:    92040000
#    nHashType:    01000000
def get_preimage_list_p2sh_p2wpkh(mptr: mmap, privkey_list: list, input_txns: list):
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        sighash_all = binascii.unhexlify('%08x' % 0x01)[::-1]

        hash_prevouts, hash_sequence, outpoints, sequences, hash_outs, locktime_b = get_preimage_hashes(mptr)

        preimage_list = []
        sequence = None
        input_count = getInputCountFromTxn(mptr)

        for index in range(input_count):
                amount_b = btc2bytes(input_txns[index]['value'])
                pubkey_b = pubkey_address.privkeyWif2pubkey(privkey_list[index])
                hash160_b = hash_utils.hash160(pubkey_b)
                script = bytes([0x76, 0xa9, len(hash160_b)]) + hash160_b + bytes([0x88, 0xac])
                script_size_b = bytes([len(script)])
                preimage = version + hash_prevouts + hash_sequence + outpoints[index] + script_size_b + script + amount_b + sequences[index] + hash_outs + locktime_b + sighash_all
                preimage_list.append(preimage)
        return preimage_list

def sign_raw_txn(mptr:mmap, address_privkey_map: dict, input_txns: list):
        prev_ptr = mptr.tell()
        mptr.seek(0)
        signed_txn = b''
        estimated_txn_size = estimateSignedTxnSize(mptr)

        print('estimated txn size = %d' % estimated_txn_size)

        sign_helper = getTxnReqIndexesForSigning(mptr)

        privkey_wif_list = [address_privkey_map[in_txn['address']] for in_txn in input_txns]

        preimage_list = get_preimage_list_p2sh_p2wpkh(mptr, privkey_wif_list, input_txns)

        mptr_read = mptr.read(sign_helper['segwit_marker']['loc'])
        signed_txn += mptr_read + b'\x00\x01'

        segwit_b = b''
        for index in range(len(input_txns)):
                in_txn = input_txns[index]
                privkey_wif = address_privkey_map[in_txn['address']]
                pubkey_b = pubkey_address.privkeyWif2pubkey(privkey_wif)
                hash160_b = hash_utils.hash160(pubkey_b)
                script_b = b'\x00\x14' + hash160_b
                script_size_b = bytes([len(script_b)])
                scriptsig_b = script_size_b + script_b
                scriptsig_size_b = bytes([len(scriptsig_b)])

                mptr_read = mptr.read(sign_helper['signatures'][index]['loc'])
                signed_txn += mptr_read + scriptsig_size_b + scriptsig_b
                mptr_read = mptr.read(1)

                witness_count_b = b'\x02'
                sign_b = sign_txn_input(preimage_list[index], privkey_wif)
                witness1_size_b = bytes([len(sign_b)])
                witness1_b = sign_b
                witness2_size_b = bytes([len(pubkey_b)])
                witness2_b = pubkey_b
                segwit_b += witness_count_b + witness1_size_b + witness1_b + witness2_size_b + witness2_b

        mptr_read = mptr.read(sign_helper['segwit']['loc'])
        signed_txn += mptr_read + segwit_b + mptr.read(4)

        mptr.close()

        print('signed txn = %s' % bytes.decode(binascii.hexlify(signed_txn)))

        return signed_txn

def return_signed_txn(jsonobj: dict, address_privkey_map: dict):
        raw_txn_s = jsonobj['Raw txn']
        mptr = mmap.mmap(-1, len(raw_txn_s) + 1)
        mptr.write(binascii.unhexlify(raw_txn_s))
        mptr.seek(0)

        input_txns = jsonobj['Inputs']

        signed_txn = sign_raw_txn(mptr, address_privkey_map, input_txns)

        jsonobj['Signed Txn'] = bytes.decode(binascii.hexlify(signed_txn))

        return jsonobj
