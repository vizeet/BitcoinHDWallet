##################
#MIT License
#
#Copyright (c) 2018 vizeet srivastava
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
##################

import binascii
import hashlib
from utility_adapters import hash_utils
from ecdsa import SigningKey, SECP256k1

# uncompressed public key has b'\x04' prefix

class CryptoUtility:
        def __init__(self, nettype: str, crypto: str):
                self.nettype = nettype
                self.crypto = crypto
                if crypto == 'bitcoin':
                        from utility_adapters import bitcoin_base58 as coin_base58
                elif crypto == 'litecoin':
                        from utility_adapters import litecoin_base58 as coin_base58
                self.coin_base58 = coin_base58

        def compressPubkey(self, pubkey: bytes):
                x_b = pubkey[1:33]
                y_b = pubkey[33:65]
                if (y_b[31] & 0x01) == 0: # even
                        compressed_pubkey = b'\x02' + x_b
                else:
                        compressed_pubkey = b'\x03' + x_b
                return compressed_pubkey

        def privkeyHex2pubkey(self, privkey_s: str):
                compress = False
                if len(privkey_s) == 66:
                        privkey_s = privkey_s[0:64]
                        compress = True
                privkey_i = int(privkey_s, 16)
                return self.privkey2pubkey(privkey_i, compress)

        def privkey2pubkey(self, privkey: int, compress = True):
                privkey_s = '%064x' % privkey
                if privkey_s.__len__() % 2 == 1:
                        privkey_s = "0{}".format(privkey_s)

                privkey_b = binascii.unhexlify(privkey_s)
                sk = SigningKey.from_string(privkey_b, curve=SECP256k1)
                vk = sk.get_verifying_key()

                pubkey_b = b'\x04' + vk.to_string()
                if compress == True:
                        pubkey_b = self.compressPubkey(pubkey_b)

                return pubkey_b

        def privkey2Wif(self, privkey: int, compress = True):
                wif = self.coin_base58.encodeWifPrivkey(privkey, self.nettype, compress)
                return wif

        def privkeyWif2Hex(self, privkey: str):
                nettype, prefix, privkey_s, for_compressed_pubkey = self.coin_base58.decodeWifPrivkey(privkey)
                if privkey_s.__len__() % 2 == 1:
                        privkey_s = "0{}".format(privkey_s)
                return privkey_s

        def privkeyWif2pubkey(self, privkey: str):
                privkey_s = self.privkeyWif2Hex(privkey)
                pubkey = self.privkeyHex2pubkey(privkey_s)
                return pubkey

        def pkh2address(self, pkh: bytes):
                address = self.coin_base58.forAddress(pkh, self.nettype, False)
                return address

        def sh2address(self, sh: bytes):
                address = self.coin_base58.forAddress(sh, self.nettype, True)
                return address

        def pubkey2address(self, pubkey: bytes):
                pkh = hash_utils.hash160(pubkey)
                print('pkh = %s' % bytes.decode(binascii.hexlify(pkh)))
                address = self.pkh2address(pkh)
                return address
