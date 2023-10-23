'''
xpykg: a script to automate install/update/uninstall for Windows XP  
'''

from json import loads, dumps
from requests import get
from requests.exceptions import MissingSchema, ConnectionError, ConnectTimeout
from sys import argv, exit
from os import system, mkdir, getenv
from os.path import isfile, isdir

xpkg_version = "0.1"

def sync_database():
    '''
    sync_database(): downloads database from github and dumps to Program Files  
    '''
    if isfile("C:\\Program Files\\xpykg\\db.json") == False:
        if isdir("C:\\Program Files\\xpykg") == False:
            mkdir("C:\\Program Files\\xpykg")

        print("[xpykg:info]: downloading database")
        with open("C:\\Program Files\\xpykg\\db.json", 'w') as xpkg_db:
            try:
                info = get("https://raw.githubusercontent.com/abrik1/xpykg/main/db.json")
                xpkg_db.write(info.content.decode('utf-8'))
                xpkg_db.close()
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("[xpykg:error]: database failed to download.. maybe try again later")
                xpkg_db.close()
                exit(1)
        print("[xpykg:info]: database written")
    else:
        with open("C:\\Program Files\\xpykg\\db.json", 'r+') as xpkg_db:
            try:
                info = get("https://raw.githubusercontent.com/abrik1/xpkg/main/db.json")
                if xpkg_db.read() == info.content.decode('utf-8'):
                    print("[xpykg:info]: database up to date")
                    xpkg_db.close()
                else:
                    xpkg_db.seek(0)
                    xpkg_db.write(info.content.decode('utf-8'))
                    xpkg_db.truncate()
                    xpkg_db.close()
                    print("[xpkg:info]: database updated")
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("[xpykg:error]: database failed to download.. maybe try again later")
                xpkg_db.close()
                exit(1)
        
def list_packages():
    '''
    list_packages(): shows the list of packages
    '''
    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", 'r') as db:
            contents = loads(db.read())
            for i in list(contents.keys()):
                print("{} {}".format(i , contents[i]['version']))
        db.close()
    else:
        print("[xpykg:error]: package index not found.. maybe sync the database to fix it")

def search_packages(query: str):
    '''
    search_packages(query: str): search packages matching to query  
    '''

    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", 'r') as db:
            contents = loads(db.read())
            count = 0
            for i in list(contents.keys()):
                matching = []
                for j in range(0, len(query)):
                    if query[j] in i:
                        matching.append(query[j])
                    else:
                        continue

                if len(matching) == len(query):
                    count = count + 1
                    print("{} {}".format(i, contents[i]['version']))

            if count == 0:
                print("[xpykg:error] no pkgs similar to {}".format(query))            
        db.close()
    else:
        print("[xpykg:error]: database not found.. maybe sync it.")

def install_package(package: str):
    '''
    install_package(package): install package to  
    '''

    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", 'r') as db:
            contents = loads(db.read())
            
            if package not in list(contents.keys()):
                print("[xpykg:error] package {} not found in database.. maybe sync database or search it".format(package))
                db.close()
                exit(1)

            print("[xpkg:info]: downloading setup.exe for package {}".format(package))
             
            try:
                exe_contents = get(contents[package]['source'])
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("[xpkg:error]: setup.exe for package {} failed to download.. maybe try again later".format(package))
                exit(1)

            # Windows executables can either be in .exe or in .msi 
            # the code below determines the source file is an .exe or a .msi and saves according to it

            if contents[package]['source'].split('.')[len(contents[package]['source'].split('.'))-1] == 'exe':
                with open("{}\\setup.exe".format(getenv("Temp")), 'wb') as setup:
                    setup.write(exe_contents.content)
                setup.close()

                print("[xpykg:note]: running installer for package {}".format(package))
                if system("{}\\setup.exe".format(getenv("Temp"))) != 0:
                    print("[xpykg:error]: {} failed to install... maybe try later".format(package))
                    exit(1)
                else:
                    print("[xpykg:sucess]: {} installed sucesfully".format(package))
                    append_to_install(package, contents[package]['version'], contents[package]['remover'])
                    exit(0)
                    
            elif contents[package]['source'].split('.')[len(contents[package].split('.'))-1] == 'msi':
                with open("{}\\setup.msi".format(getenv("Temp")), 'wb') as setup:
                    setup.write(exe_contents.content)
                setup.close()

                if system("{}\\setup.msi".format(getenv("Temp"))) != 0:
                    print("[xpykg:error]: {} failed to install".format(package))
                else:
                    print("[xpykg:sucess]: {} instaled sucessfully".format(package))
                    append_to_install(package, contents[package]['version'], contents[package]['remover'])
                    exit(0)
    else:
        print("[xpykg:error]: package index not found.. maybe run sync")

def append_to_install(pkgname: str, version: str, remover: str):
    '''
    append_to_install(pkgname, version, remover): append package to install database
    '''
    if isfile("C:\\Program Files\\xpykg\\installed-packages") == False:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'w') as db:
            db.write("{} {} {}\n".format(pkgname, version, remover))
        db.close()
    else:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'a+') as db:
            db.write("{} {} {}\n".format(pkgname, version, remover))
        db.close()
        
if __name__ == "__main__":
    try:
        if argv[1] in ["-h", "help", "--help"]:
            print('''xpykg: a script for software management for Windows XP
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
            print("[xpkg:version]: {}".format(xpkg_version))
        elif argv[1] in ["-S", "sync", "--sync"]:
            sync_database()
        elif argv[1] in ["-l", "list", "--list"]:
            list_packages()
        elif argv[1] in ["-s", "search", "--search"] and len(argv) == 3:
            search_packages(argv[2])
        elif argv[1] in ["-i", "install", "--install"]:
            if len(argv) == 3:
                install_package(argv[2])
        else:
            print("[xpykg:error]: invalid argument or not sufficient arguements")
    except IndexError:
        print("[xpykg:error]: invalid argument or not sufficient arguments")
    except KeyboardInterrupt:
        print("[xpykg:error]: keyboard exit detected")
        exit(1)
