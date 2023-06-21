#!/usr/bin/env bash

__ScriptVersion="version"

#===  FUNCTION  ================================================================
#         NAME:  usage
#  DESCRIPTION:  Display usage information.
#===============================================================================
function usage ()
{
  echo "Usage :  $0 [options] [--]

    Options:
    -h|help       Display this message
    -v|version    Display script version
    -c|cdrom      ISO to use
    -d|drive      disk to use"

}    # ----------  end of function usage  ----------

#-----------------------------------------------------------------------
#  Handle command line arguments
#-----------------------------------------------------------------------

[ $# -lt 4 ] && usage && exit 1

while getopts ":hvc:d:" opt
do
  case $opt in

  h|help     )  usage; exit 0 ;;

  v|version  )  echo "$0 -- Version $__ScriptVersion"; exit 0 ;;

  c|cdrom  )  CDROM="$OPTARG";;

  d|drive  )  DRIVE="$OPTARG" ;;

  * )  echo -e "\n  Option does not exist : $OPTARG\n"
      usage; exit 1   ;;

  esac    # --- end of case ---
done
shift $(($OPTIND-1))

echo "Launching qemu with CDROM=${CDROM} and DRIVE=${DRIVE}"

qemu-system-x86_64 \
  -enable-kvm \
  -m 16000 \
  -smp 8 \
  -cdrom "$CDROM" \
  -nographic \
  -drive file="$DRIVE",format=raw \
  -netdev user,id=ssh_net,hostfwd=tcp:127.0.0.1:17777-:22 \
  -device e1000,netdev=ssh_net \
  -bios /usr/share/edk2-ovmf/OVMF_CODE.fd \
  -cpu base,\
+de,\
+msr,\
+xgetbv1,\
+tsc,\
+pdpe1gb,\
+fsgsbase,\
+rdrand,\
+ht,\
+erms,\
+vmx,\
+xsave,\
+sse,\
+syscall,\
+sep,\
+sse2,\
+sse4.1,\
+sse4.2,\
+rdseed,\
+fpu,\
+apic,\
+pat,\
+ibrs,\
+pbe,\
+lm,\
+popcnt,\
+cmov,\
+xsavec,\
+ibpb,\
+mca,\
+mce,\
+monitor,\
+vme,\
+mmx,\
+stibp,\
+pclmulqdq,\
+smep,\
+mpx,\
+cx8,\
+pae,\
+ss,\
+tm,\
+x2apic,\
+smap,\
+pse,\
+pge,\
+acpi,\
+dtes64,\
+ssse3,\
+clflush,\
+fxsr,\
+ssbd,\
+pse36,\
+nx,\
+rdtscp,\
+xsaveopt,\
+xtpr,\
+movbe,\
+3dnowprefetch,\
+pni,\
+aes,\
+arat,\
+tm2,\
+cx16,\
+pdcm,\
+est,\
+mtrr,\
+xsaves,\
+clflushopt
