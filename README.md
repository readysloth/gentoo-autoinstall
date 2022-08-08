# gentoo autoinstall

This repo is improvement of [previous attempt](https://github.com/readysloth/Workspace-recreation)
to create autoinstall scripts, that would roll out my workspace configuration.


## How can it be useful for you

These scripts provide:

- Better logging of install process
- Resuming of interrupted installation
- (TODO) Binary installation instead of compiling
- Common USE-flags specification before installation
- More flexible configuration
- Easy tweaking

## Run

```
usage: install.py [-h] [-n] [-b] [-v] [-c [CPU]] [-i [INIT]]
                  [-u USE_FLAGS [USE_FLAGS ...]] [-t] [-T] [-p]
                  [-H [HOST_NAME]] [-U [USER]] [-r]
                  disk

Gentoo workspace installer

positional arguments:
  disk                  dev node to install gentoo

optional arguments:
  -h, --help            show this help message and exit
  -n, --dry-run         pretend to install, do nothing actually
  -b, --prefer-binary   prefer binary packages to source
  -v, --verbose         enable debug logging
  -c [CPU], --cpu [CPU]
                        cpu architecture
  -i [INIT], --init [INIT]
                        init system
  -u USE_FLAGS [USE_FLAGS ...], --use-flags USE_FLAGS [USE_FLAGS ...]
                        system-wide use flags
  -t, --no-gui          install only terminal packages
  -T, --no-wm           install only terminal packages and X server
  -p, --no-packages     do not install any supplied packages
  -H [HOST_NAME], --host-name [HOST_NAME]
                        OS hostame
  -U [USER], --user [USER]
                        user name
  -r, --resume          executed.actions file for installation resume
```

## Example install

```
wget https://raw.githubusercontent.com/readysloth/gentoo-autoinstall/main/easy_install.sh
bash easy_install.sh
```
