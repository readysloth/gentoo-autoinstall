#!/bin/sh

wget "https://raw.githubusercontent.com/readysloth/gentoo-autoinstall/minimal/download_scripts.sh"
. download_scripts.sh
cd $FOLDER

echo "++++++++++++++++++++++++++++++++++++++++"
echo "+ Type in disk node for gentoo install +"
echo "+         For example: /dev/sda        +"
echo "++++++++++++++++++++++++++++++++++++++++"

lsblk
printf "DISK="
read DISK

python3 install.py install -h

echo "+++++++++++++++++++++++++++"
echo "+ Specify install options +"
echo "+++++++++++++++++++++++++++"
printf "INSTALL_OPTS="
read INSTALL_OPTS

python3 install.py install $DISK $INSTALL_OPTS
