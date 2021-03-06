#############
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
#############

import hashlib
from utils import random_number_generator
import binascii
from functools import reduce
import math
import tkinter
from tkinter.ttk import Combobox
import tkinter.messagebox

top = tkinter.Tk()
message = []
word_key_list = []

def callback(i: int):
        tkinter.messagebox.showinfo( "%d" % (i+1), "%s" % word_key_list[i])
        message[i].set('Pressed')

def getChecksumBitCount(mnemonic_length: int):
        if (mnemonic_length % 3) != 0:
                raise ValueError('Invalid Mnemonic code length')
        checksum_bit_count = mnemonic_length // 3
        return checksum_bit_count

def getEntropyBitCount(mnemonic_length: int):
        if (mnemonic_length % 3) != 0:
                raise ValueError('Invalid Mnemonic code length')
        entropy_bit_count = (mnemonic_length * 32) // 3
        return entropy_bit_count

def getCheckEntropyBitCount(mnemonic_length: int):
        checksum_bit_count = getChecksumBitCount(mnemonic_length)
        entropy_bit_count = getEntropyBitCount(mnemonic_length)
        entropy_checksum_bit_count = entropy_bit_count + checksum_bit_count
        return entropy_checksum_bit_count

def getEntropyCheckBits(mnemonic_length: int):
        entropy_bit_count = getEntropyBitCount(mnemonic_length)
        random_number_b = random_number_generator.getRandomNumberBits(entropy_bit_count)
        checksum_bit_count = getChecksumBitCount(mnemonic_length)
        checksum = int(binascii.hexlify(hashlib.sha256(random_number_b).digest()), 16)
        initial_checksum = checksum >> (256 - checksum_bit_count)
        random_number = int(bytes.decode(binascii.hexlify(random_number_b)), 16)
        shifted_random_number = random_number << checksum_bit_count
        entropy_check_i = shifted_random_number | initial_checksum
        entropy_check_size_bytes = math.ceil((entropy_bit_count + checksum_bit_count) / 8)
        entropy_check_s = ('%x' % entropy_check_i).zfill(entropy_check_size_bytes * 2)
        entropy_check_b = binascii.unhexlify(entropy_check_s)
        return entropy_check_b

def getMnemonicWordList():
        word_list = []
        with open('utils/mnemonic_word_list_english.txt', 'rt') as word_file:
                word_list = word_file.read().splitlines()
        return word_list

def entropyCheckBits2List(entropy_check_b: bytes, size: int):
        selector_int = int(binascii.hexlify(entropy_check_b), 16)
        selector_list = []
        while size >= 11:
                selector_list.append(selector_int & 0x07FF)
                selector_int = selector_int >> 11
                size -= 11
        return selector_list[::-1]

def getEntropyCheckBitCountFromSelectorCount(selector_count: int):
        return selector_count * 11

def getChecksumBitCountFromEntropyBitCount(entropy_bit_count: int):
        return entropy_bit_count // 32

def convertSelectorList2Bits(selector_list: list):
        entropy_check_bit_count = getEntropyCheckBitCountFromSelectorCount(len(selector_list))
        entropy_check_i = reduce(lambda x, y: (x << 11) | y, selector_list)
        return entropy_check_i

def getMnemonicWordCodeString(mnemonic_length: int):
        word_list = getMnemonicWordList()
        entropy_check_bit_count = getCheckEntropyBitCount(mnemonic_length)
        entropy_check_b = getEntropyCheckBits(mnemonic_length)
        selector_list = entropyCheckBits2List(entropy_check_b, entropy_check_bit_count)
        mnemonic_word_list = getMnemonicWordList()
        word_key_list = [mnemonic_word_list[selector] for selector in selector_list]

        return word_key_list

def verifyChecksumInSelectorBits(entropy_check_i: int, mnemonic_length: int):
        entropy_bit_count = getEntropyBitCount(mnemonic_length)
        checksum_bit_count = getChecksumBitCount(mnemonic_length)
        entropy_i = (entropy_check_i >> checksum_bit_count)
        entropy_size_bytes = entropy_bit_count // 8
        entropy_s = ('%x' % entropy_i).zfill(entropy_size_bytes * 2)
        entropy_b = binascii.unhexlify(entropy_s)
        set_bits = (1 << checksum_bit_count) - 1
        initial_checksum = entropy_check_i & set_bits
        checksum_calculated = int(bytes.decode(binascii.hexlify(hashlib.sha256(entropy_b).digest())), 16)
        initial_checksum_calculated = (checksum_calculated >> (256 - checksum_bit_count))
        return (initial_checksum_calculated == initial_checksum)

def verifyMnemonicWordCodeString(mnemonic_code: str):
        word_key_list = mnemonic_code.split()
        mnemonic_length = len(word_key_list)
        mnemonic_word_list = getMnemonicWordList()
        selector_list = [mnemonic_word_list.index(word) for word in word_key_list]
        entropy_check_i = convertSelectorList2Bits(selector_list)
        return verifyChecksumInSelectorBits(entropy_check_i, mnemonic_length)

if __name__ == '__main__':
        word_key_list = getMnemonicWordCodeString(12)
        top.title("MNEMONIC CODES")
        top.grid_rowconfigure(1,weight=1)
        top.grid_columnconfigure(1,weight=1)

        frame = tkinter.Frame(top)
        frame.pack(fill=tkinter.X, padx=5, pady=5)

        for y in range(0,12):
                message.append(tkinter.StringVar())
                message[y].set('Not pressed.')
                b = tkinter.Button(frame, textvariable=message[y],   command=lambda y=y: callback(y))
                b.grid(row=0,column=y)

        top.mainloop()

        joined_word_key_list = ' '.join(word_key_list)

        print('is valid = %r' % verifyMnemonicWordCodeString(joined_word_key_list))
