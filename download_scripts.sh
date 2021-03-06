#!/bin/sh

SCRIPTS="
bootstrap.py
common.py
disk_ops.py
entity.py
install.py
install_logger.py
packages.py
partitioning.py
system_install.py"

FOLDER=installation_scripts

mkdir $FOLDER
cd $FOLDER
  for script in $SCRIPTS
  do
    wget "https://raw.githubusercontent.com/readysloth/gentoo-autoinstall/main/$script"
  done
cd -

echo "++++++++++++++++++++++"
echo "+Download is complete+"
echo "++++++++++++++++++++++"
echo
echo "Go to folder '$FOLDER' and run 'install.py'"
