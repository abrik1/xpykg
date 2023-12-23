## xpykg - manage software packages for Windows XP
xpykg is a script for Windows XP which is capable of installing software
packages so that users don't have to look on random webpages for software.

xpykg downloads the setup.exe of the software package and then runs it.
It also keeps track of the location of the uninstaller executable so that
the user may easily uninstall the package when they need to.

### requirements:
- Python 3.4
 - requests 2.20
 - colorama (colors are cool)
 - wmi (for Un_A.exe detection)

**NOTE**: Right now it works only on Service Pack 3 for x86 and Service Pack 2 for x64 (DB needs some changes).

### todo:
- [x] implement search
- [x] implement sync
- [x] implement list
- [x] implement installing via msi or exe
- [x] implement uninstalling
 - WIP, needs some more testing
- [x] implement upgrading 
 - add support to again upgrade packages which failed to upgrade in last run

### software:
see db.json

## docs:
see [the wiki](https://github.com/abrik1/xpykg/wiki)

# contact:
Join the `#xpykg` channel on irc.libera.chat, or see the [${\color{purple}discord\ server\colon}$](https://discord.gg/5Jwd7Sch88)
