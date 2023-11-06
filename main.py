'''
xpykg: a script to automate install/update/uninstall for Windows XP  
'''

from json import loads, dumps
from requests import get
from requests.exceptions import MissingSchema, ConnectionError, ConnectTimeout
from sys import argv, exit
from os import system, mkdir, getenv, chdir
from os.path import isfile, isdir
from ast import literal_eval

xpykg_version = "0.1"

def sync_database(): 
    '''
    sync_database(): downloads database from github and dumps to Program Files  
    '''
    if isfile("C:\\Program Files\\xpykg\\db.json") == False:
        if isdir("C:\\Program Files\\xpykg") == False:
            mkdir("C:\\Program Files\\xpykg")

        print("[xpykg:info]: downloading database")
        with open("C:\\Program Files\\xpykg\\db.json", 'w') as xpykg_db:
            try:
                info = get("https://raw.githubusercontent.com/abrik1/xpykg/main/db.json")
                xpykg_db.write(info.content.decode('utf-8'))
                xpykg_db.close()
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("[xpykg:error]: database failed to download.. maybe try again later")
                xpykg_db.close()
                exit(1)
        print("[xpykg:info]: database written")
    else:
        with open("C:\\Program Files\\xpykg\\db.json", 'r+') as xpykg_db:
            try:
                info = get("https://raw.githubusercontent.com/abrik1/xpykg/main/db.json")
                if xpykg_db.read() == info.content.decode('utf-8'):
                    print("[xpykg:info]: database up to date")
                    xpykg_db.close()
                else:
                    xpykg_db.seek(0)
                    xpykg_db.write(info.content.decode('utf-8'))
                    xpykg_db.truncate()
                    xpykg_db.close()
                    print("[xpykg:info]: database updated")
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("[xpykg:error]: database failed to download.. maybe try again later")
                xpykg_db.close()
                exit(1)
        
def list_packages():
    '''
    list_packages(): shows the list of packages
    '''
    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", 'r') as db:
            contents = loads(db.read())
            for i in list(contents.keys()):
                if is_installed(i) == True:
                    print("{} {} [installed by xpykg]".format(i , contents[i]['version']))
                else:
                    print("{} {}".format(i, contents[i]['version']))
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
                    if is_installed(i) == True:
                        print("{} {} [installed by xpykg]".format(i, contents[i]['version']))
                    else:
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

            print("[xpykg:info]: downloading setup.exe for package {}".format(package))
             
            try:
                exe_contents = get(contents[package]['source'])
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("[xpykg:error]: setup.exe for package {} failed to download.. maybe try again later".format(package))
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
            db.write("{}\n".format([pkgname, version, remover]))
        db.close()
    else:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'a+') as db:
            db.write("{}\n".format([pkgname, version, remover]))
        db.close()

def is_installed(pkgname: str):
    '''
    is_installed(pkgname) -> True/False.. this function determines that a package is installed or not
    '''
    if isfile("C:\\Program Files\\xpykg\\installed-packages") == True:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'r') as database:
            contents = database.read()
            for i in contents.splitlines():
                if literal_eval(i)[0] == pkgname:
                    database.close()
                    return True
                
        database.close()
        return False
    else:
        return False

def arr_to_str(arr, optchar: str):
    '''
    arr_to_str().. converts
    '''
    nstr = ""
    for i in arr:
        nstr = nstr+i+optchar

    return nstr

def uninstall_package(pkgname: str):
    '''
    uninstall_package(pkgname): remove pkgname if installed by xpykg  
    '''
    if is_installed(pkgname) == True:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'r+') as ipkg:
            contents = ipkg.read().splitlines()
            index = 0
            remover = ""
            for i in contents:
                if literal_eval(i)[0] == pkgname:
                    index = contents.index(i)
                    remover = literal_eval(i)[2]
                    break
                
            remove = remover.split("\\")
            remove.pop(len(remove)-1)
            chdir(arr_to_str(remove, "\\"))
            
            remover = remover.split("\\")[len(remover.split("\\"))-1]
            
            if system(remover) == 0:
                contents.pop(index)
                ncontent = ""
                for j in contents:
                    ncontent = ncontent+j
                
                ipkg.seek(0)
                ipkg.write(ncontent)
                ipkg.truncate()
                ipkg.close()
                print("[xpykg:sucess]: package {} removed".format(pkgname))
                return 0
            else:
                print("[xpykg:error]: {} not removed".format(pkgname))
                ipkg.close()
                return 1 
    else:
        print("[xpykg:error]: package {} not installed".format(pkgname))
        return 1
        
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
upgrade: upgrade packages installed using xpykg
version: show xpykg version''')
        elif argv[1] in ["-v", "version", "--version"]:
            print("[xpykg:version]: {}".format(xpykg_version))
        elif argv[1] in ["-S", "sync", "--sync"]:
            sync_database()
        elif argv[1] in ["-l", "list", "--list"]:
            list_packages()
        elif argv[1] in ["-s", "search", "--search"] and len(argv) == 3:
            search_packages(argv[2])
        elif argv[1] in ["-i", "install", "--install"]:
            if len(argv) == 3:
                install_package(argv[2])
        elif argv[1] in ["-u", "uninstall", "--uninstall"]:
            if len(argv) == 3:
                uninstall_package(argv[2])
        else:
            print("[xpykg:error]: invalid argument or not sufficient arguements")
    except IndexError:
        print("[xpykg:error]: invalid argument or not sufficient arguments")
    except KeyboardInterrupt:
        print("[xpykg:error]: keyboard exit detected")
        exit(1)
