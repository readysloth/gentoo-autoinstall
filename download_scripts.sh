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
system_install.py
create_configs.sh"

FOLDER=installation_scripts

mkdir $FOLDER
cd $FOLDER
  for script in $SCRIPTS
  do
    wget "https://raw.githubusercontent.com/readysloth/gentoo-autoinstall/mango-pi/scripts/$script"
  done
cd -

echo "++++++++++++++++++++++++"
echo "+ Download is complete +"
echo "++++++++++++++++++++++++"
echo
echo "Go to folder '$FOLDER' and run 'install.py'"
