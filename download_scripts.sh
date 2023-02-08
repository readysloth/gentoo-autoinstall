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
create_configs.sh
configs/boot.cmd
configs/u-boot.config
configs/gentoo-kernel-6.1.8.config
configs/patches/power.patch
configs/patches/power.dtb.patch
configs/patches/arm64-dts-allwinner-h616-Add-device-node-for-SID.patch
configs/patches/arm64-dts-allwinner-h616-Add-thermal-sensor-and-thermal-zones.patch
configs/patches/arm64-dts-allwinner-sun50i-h616-Add-GPU-node.patch
"


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
