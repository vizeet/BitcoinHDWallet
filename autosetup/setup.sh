#!/bin/bash
cp -Rf /media/ubuntu/CDROM/* /tmp
chmod 775 /tmp/autosetup
chmod 775 /tmp/SimpleBitcoinWallet
sudo apt install -y /tmp/autosetup/libexpat1-dev_2.1.0-7ubuntu0.16.04.3_amd64.deb
sudo apt install -y /tmp/autosetup/libpython3.5-dev_3.5.2-2ubuntu0~16.04.5_amd64.deb
sudo apt install -y /tmp/autosetup/libpython3-dev_3.5.1-3_amd64.deb
sudo apt install -y /tmp/autosetup/python3.5-dev_3.5.2-2ubuntu0~16.04.5_amd64.deb
sudo apt install -y /tmp/autosetup/python3-dev_3.5.1-3_amd64.deb
sudo apt install -y /tmp/autosetup/python3-setuptools_20.7.0-1_all.deb
sudo apt install -y /tmp/autosetup/tk8.6-blt2.5_2.5.3+dfsg-3_amd64.deb
sudo apt install -y /tmp/autosetup/blt_2.5.3+dfsg-3_amd64.deb
sudo apt install -y /tmp/autosetup/python3-tk_3.5.1-1_amd64.deb
sudo apt install -y /tmp/autosetup/python-pip-whl_8.1.1-2ubuntu0.4_all.deb
sudo apt install -y /tmp/autosetup/python3-wheel_0.29.0-1_all.deb
sudo apt install -y /tmp/autosetup/python3-pip_8.1.1-2ubuntu0.4_all.deb 
pip3 install --user /tmp/autosetup/pygame-1.9.5-cp35-cp35m-manylinux1_x86_64.whl
pip3 install --user /tmp/autosetup/PyQRCode-1.2.1.tar.gz
