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
configs/patches/arm64-dts-allwiner-sun50i-h616.dtsi-add-usb-ehci-ohc.patch
configs/patches/arm64-dts-allwinner-sun50i-h616-Add-VPU-node.patch
configs/patches/orangepizero2_dts_set_bldo2_to_1.8v.patch
configs/patches/hdmi.dtb.patch
configs/patches/cpu-opp-table.dtb.patch
configs/patches/dma.dtb.patch
configs/patches/ethernet.dtb.patch
configs/patches/hdmi_audio.dtb.patch
configs/patches/pwm.dtb.patch
configs/patches/sunxi-info.dtb.patch
configs/patches/thermal.dtb.patch
configs/patches/gpu.dtb.patch
configs/patches/sram.dtb.patch
configs/patches/ths-workaround.uboot.patch
configs/patches/r_rsb-to-r_i2c.patch
configs/patches/axp1530-u-boot.patch
configs/patches/new-thermal-trips.dtb.patch
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
