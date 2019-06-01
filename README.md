# BitcoinHDWallet

BitcoinHDWallet is an offline bitcoin wallet based on Hierarchical Deterministic Wallet BIP32 implementation. It works with its Online counter part project OnlineWalletP2SH_P2WPKH.

Installation instruction currently covers only Linux environment.

>> Disclaimer: Code is well tested and tested with my own funds. But no testing is complete without third party user. Use the wallet at your own risk and keep smaller funds in each address. 

## Features
1. Easy setup: Does not require extra computer or special device.
2. Secure: As transaction signing happens offline. At no point private-key is printed or provided. Secret is not stored. 
3. Open source and mostly uses bitcoin-core wallet.
4. Smart Fee estimation: Uses bitcoin-cli command "estimatefeeestimate" to calculate fee for transaction.
5. Privacy: Does not use SPVs. And Uses all transactions associated with one address when creating a new transaction. This prevents exposure of public keys which may help in tracking transaction or can be attacked by quantum computers in future.
6. Low fee: Uses Segwit wrapped in Pay-to-script hash i.e. P2SH-P2WPKH address. Which saves on network fee.

## Installation
Requires two USB drives:
1. Ubuntu 16.04 live image iso (Minimum 4GB)
1. Contains two partitions:
   1. ISO image of code
   1. For data

Steps:
1. Clone code
```bash
git clone https://github.com/vizeet/BitcoinHDWallet.git
cd BitcoinHDWallet
```
2. To create ISO image of code 
```bash
./prepare_iso.sh
```
3. Create USB for code and data
You can use any partition manager to create two partition. 
   1. Create empty partition (requires less than 100mb space) for code and copy iso to the partition.
   2. Create ext4/fat32 partition with a label

```bash
sudo dd if=disk.iso of=/dev/<partition 1>
```

4. Boot using ubuntu usb and try out the OS

5. Mount code and data partitions and cd into code
```bash
cd /media/ubuntu/CDROM
```

6. Setup environment:
```bash
cd autosetup
./setup
cd /tmp
source ./setenv
```

7. Update wallet configuration:
```bash
cd config
cp hd_wallet.config.template hd_wallet.config
```
```json
{
"salt": <provide and remember salt>,
"network": "mainnet",
"datadir": <data dir path>
}
```
> Remember salt which will be required for generating privkey.
Please make sure datadir has correct permissions.

8. Setup online wallet on main computer using instructions from
git project "OnlineWalletP2SH_P2WPKH" 

## Usage
>> Generation and use of mnemonic code (secret code) uses tkinter gui in order to avoid risk of accidently coping it in a storage. Please note mnemonic code on paper or memorize it.
1. In offline Ubuntu: Follow setup instructions 6 & 7

2. Generate Mnemonic code:
```bash
cd /tmp/src
python3 mnemonic_code.py
```
This will open widget with 12 buttons. On pressing each button a word will appear. After closing widgets on commandline it will inform whether the secret is valid or not. This is extra checking and should never be invalid. But incase it does please generate secret again.
>These 12 words are secret and must be kept secret. Also remember the salt given in hd_wallet.config

3. Generate bitcoin addresses:
```bash
python3 wallet_main.py [-t]
```
-t is for running in test mode
> Fill the mnemonic code in widget. Any mistake during filling will give error. And if mnemonic code is wrong it will print error in commandline.
Next it will ask to fill first and the last selector. Format is : m/a/b/c/...
Start is m/../1 and end is m/../100.(example m/5/1 to m/5/100). I think range is upto 32000. 
Select option 1 to generate address

4. Validate addresses and Generate raw transaction from online wallet.

5. Sign raw transaction:
```bash
python3 wallet_main.py [-t]
```
After filling mnemonic and selector range. select 2 for signing raw transaction.

6. Publish this signed transaction which appears in "transaction_info.json". Either using online wallet or any web utility.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
