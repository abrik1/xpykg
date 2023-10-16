'''
xpkg: a script to automate install/update/uninstall for Windows XP
'''

from json import loads, dumps
from requests import get
from requests.exceptions import MissingSchema, ConnectionError, ConnectTimeout
from sys import argv, exit
from os import system
from os.path import isfile, isdir

xpkg_version = "0.1"

if __name__ == "__main__":
    try:
        if argv[1] in ["-h", "help", "--help"]:
            print('''xpkg: a script for software management for Windows XP
=====================================================
help: view this page
install: install <pkg>
list: show all the available apps
search: search <pkg>
sync: sync software databases
uninstall: uninstall <pkg>
upgrade: upgrade packages installed using xpkg
version: show xpkg version''')
        elif argv[1] in ["-v", "version", "--version"]:
            print("xpkg {}".format(xpkg_version))
    except IndexError:
        print("[xpkg:error]: invalid argument")
