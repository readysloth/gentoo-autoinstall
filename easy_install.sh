#!/bin/sh

wget "https://raw.githubusercontent.com/readysloth/gentoo-autoinstall/main/download_scripts.sh"
. download_scripts.sh
cd $FOLDER

echo "++++++++++++++++++++++++++++++++++++++++"
echo "+ Type in disk node for gentoo install +"
echo "+         For example: /dev/sda        +"
echo "++++++++++++++++++++++++++++++++++++++++"

lsblk
printf "DISK="
read DISK

python3 install.py -h

echo "+++++++++++++++++++++++++++"
echo "+ Specify install options +"
echo "+++++++++++++++++++++++++++"
printf "INSTALL_OPTS="
read INSTALL_OPTS

python3 install.py $DISK $INSTALL_OPTS
