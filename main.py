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
from colorama import init, Fore, Style
from wmi import WMI
from time import sleep

xpykg_version = "0.1" 
init() # initialize colorama
wmi = WMI()

def sync_database(): 
    '''
    sync_database(): downloads database from github and dumps to Program Files  
    '''
    if isfile("C:\\Program Files\\xpykg\\db.json") == False:
        if isdir("C:\\Program Files\\xpykg") == False:
            mkdir("C:\\Program Files\\xpykg")

        print("{}{}[xpykg:info]{}: downloading database".format(Style.BRIGHT, Fore.BLUE, Fore.RESET))
        with open("C:\\Program Files\\xpykg\\db.json", 'w') as xpykg_db:
            try:
                info = get("https://raw.githubusercontent.com/abrik1/xpykg/main/db.json")
                xpykg_db.write(info.content.decode('utf-8'))
                xpykg_db.close()
                return 0
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("{}{}[xpykg:error]{}: database failed to download.. maybe try again later".format(Style.BRIGHT ,Fore.RED, Fore.RESET))
                xpykg_db.close()
                return 1
        print("{}{}[xpykg:sucess]:{} database written".format(Style.BRIGHT, Fore.GREEN, Fore.RESET))
        return 0
    else:
        with open("C:\\Program Files\\xpykg\\db.json", 'r+') as xpykg_db:
            try:
                info = get("https://raw.githubusercontent.com/abrik1/xpykg/main/db.json")
                if xpykg_db.read() == info.content.decode('utf-8'):
                    print("{}{}[xpykg:note]:{} database up to date".format(Style.BRIGHT, Fore.BLUE, Fore.RESET))
                    xpykg_db.close()
                    return 0
                else:
                    xpykg_db.seek(0)
                    xpykg_db.write(info.content.decode('utf-8'))
                    xpykg_db.truncate()
                    xpykg_db.close()
                    print("{}{}[xpykg:sucess]:{} database updated".format(Style.BRIGHT, Fore.GREEN, Fore.RESET))
                    return 0
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("{}{}[xpykg:error]:{} database failed to download.. maybe try again later".format(Style.BRIGHT, Fore.RED, Fore.RESET))
                xpykg_db.close()
                return 1
        
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
                print("{}{}[xpykg:error]:{} no pkgs similar to {}{}{}".format(Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, query, Fore.RESET))            
        db.close()
    else:
        print("{}{}[xpykg:error]:{} database not found.. maybe sync it.".format(Style.BRIGHT, Fore.RED, Fore.RESET))

def install_package(package: str):
    '''
    install_package(package): install package to  
    '''
    
    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", 'r') as db:
            contents = loads(db.read())
            
            if package not in list(contents.keys()):
                print("{}{}[xpykg:error]:{} package {}{}{} not found in database.. maybe sync database or search it".format(Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, package, Fore.RESET))
                db.close()
                return 1

            print("{}{}[xpykg:info]:{} downloading setup.exe for package {}{}{}".format(Style.BRIGHT, Fore.BLUE, Fore.RESET, Fore.YELLOW, package, Fore.RESET))
             
            try:
                exe_contents = get(contents[package]['source'])
            except (MissingSchema, ConnectionError, ConnectionAbortedError, ConnectTimeout, ConnectionRefusedError, ConnectionResetError):
                print("{}{}[xpykg:error]:{} setup.exe for package {}{}{} failed to download.. maybe try again later".format(Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, package, Fore.RESET))
                return 1

            # Windows executables can either be in .exe or in .msi 
            # the code below determines the source file is an .exe or a .msi and saves according to it

            status_code = 0 # system() will take over this variable

            print("{}{}[xpykg:note]:{} running installer for package {}{}{}".format(Style.BRIGHT, Fore.BLUE, Fore.RESET, Fore.YELLOW, package, Fore.RESET))

            if contents[package]['source'].split('.')[len(contents[package]['source'].split('.'))-1] == 'exe':
                with open("{}\\setup.exe".format(getenv("Temp")), 'wb') as setup:
                    setup.write(exe_contents.content)
                setup.close() 
                status_code = system("{}\\setup.exe".format(getenv("Temp")))

            elif contents[package]['source'].split('.')[len(contents[package].split('.'))-1] == 'msi':
                with open("{}\\setup.msi".format(getenv("Temp")), 'wb') as setup:
                    setup.write(exe_contents.content)
                setup.close()

                status_code = system("{}\\setup.msi".format(getenv("Temp")))  # 0 for good exit.
    else:
        print("{}{}[xpykg:error]:{} package index not found.. maybe run sync".format(Style.BRIGHT, Fore.RED, Fore.RESET))

        # now append to install and categorize uninstallers as normal, nullsoft or custom

    if status_code == 0:
        print("{}{}[xpykg:sucess]:{} {}{}{} installed sucessfully".format(Style.BRIGHT, Fore.GREEN, Fore.RESET, Fore.YELLOW, package, Fore.RESET))
        if "isUninstallerByNullsoft" in list(contents[package].keys()): # determine nullsoft uninstallers:
            append_to_install(package, contents[package]['version'], contents[package]['remover'], "UninstallerByNullsoft")
        else: # for normal uninstallers
            append_to_install(package, contents[package]['version'], contents[package]['remover'], "Normal")

        return 0
    else:
        print("{}{}[xpykg:error]: {}{} failed to install".format(Style.BRIGHT, Fore.RED, Fore.YELLOW, Fore.RESET))
        return 1
        
def append_to_install(pkgname: str, version: str, remover: str, uninstall_type: str):
    '''
    append_to_install(pkgname, version, remover): append package to install database
    '''
    if isfile("C:\\Program Files\\xpykg\\installed-packages") == False:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'w') as db:
            db.write("{}".format([pkgname, version, remover, uninstall_type]))
        db.close()
    else:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'a+') as db:
            db.write("\n{}".format([pkgname, version, remover, uninstall_type]))
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

def get_installed_package_version(pkgname: str):
    '''
    get_installed_package_version(pkgname).. if pkgname is installed by xpykg then return which version is installed by xpykg
    '''

    if is_installed(pkgname) == True:
        with open("C:\\Program Files\\xpykg\\installed-packages", 'r') as database:
            contents = database.read().splitlines()
            for i in contents:
                if literal_eval(i)[0] == pkgname:
                    database.close()
                    return literal_eval(i)[1] # good output
    else:
        return 1 # bad output

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
            uninstall_type = ""
            for i in contents:
                if literal_eval(i)[0] == pkgname:
                    index = contents.index(i)
                    remover = literal_eval(i)[2]
                    uninstall_type = literal_eval(i)[3]
                    break
                
            remove = remover.split("\\")
            remove.pop(len(remove)-1)
            chdir(arr_to_str(remove, "\\"))
            
            remover = remover.split("\\")[len(remover.split("\\"))-1]

            print("{}{}[xpykg:note]:{} loading remover for package {}{}{}".format(Style.BRIGHT, Fore.BLUE, Fore.RESET, Fore.YELLOW, pkgname, Fore.RESET))
            remove_status = system(remover)
            pkg_removed = False 

            if remove_status == 0 and uninstall_type == "Normal":
                pkg_removed = True
                #contents.pop(index)
                #ncontent = ""
                #for j in contents:
                    #ncontent = ncontent+j

                #print(ncontent) 
                #ipkg.seek(0)
                #ipkg.write(ncontent)
                #ipkg.truncate()
                #ipkg.close()
                #print("{}{}[xpykg:sucess]:{} package {}{}{} removed".format(Style.BRIGHT, Fore.GREEN, Fore.RESET, Fore.YELLOW, pkgname, Fore.RESET))
                #return 0
            elif remove_status == 0 and uninstall_type == "UninstallerByNullsoft":
                # using wmi check that Un_a.exe is running or not
                sleep(1)
                while True:
                    prcs = [] # array to store processes running
                    for process in wmi.Win32_Process():
                        prcs.append(process.Name)

                    if not "Un_A.exe" in prcs:
                        break # assumption that it has been uninstalled..
                
                if isfile(remover) == True:
                   pkg_removed = False
                else:
                    pkg_removed = True 
            else:
                print("{}{}[xpykg:error]:{} {}{}{} not removed".format(Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, pkgname, Fore.RESET))
                ipkg.close()
                return 1 
            
            if pkg_removed == False:
                print("{}{}[xpykg:error]: {}{}{} not removed".format(Style.BRIGHT, Fore.RED, Fore.YELLOW, pkgname, Fore.RESET))
                return 1
            else:
                print("{}{}[xpykg:sucess]: {}{}{} removed".format(Style.BRIGHT, Fore.GREEN, Fore.YELLOW, pkgname, Fore.RESET))
                return 0
    else:
        print("{}{}[xpykg:error]:{} package {}{}{} not installed".format(Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, pkgname, Fore.RESET))
        return 1

def vtoi(version: str):
    '''
    vtoi(version): return version to an integer.. 22.10 -> 2210
    '''
    
    ver = ""

    for i in version:
        try:
            ver = ver+str(int(i))
        except ValueError:
            continue

    return int(ver)

def upgrade_packages():
    '''
    upgrade_packages(): this function is the main upgrade function for xpykg
    '''
    print("{}{}[xpykg:note]:{} updating database".format(Style.BRIGHT, Fore.BLUE, Fore.RESET))

    if sync_database() != 0:
        print("{}{}[xpykg:error]:{} database failed to sync".format(Style.BRIGHT, Fore.RED, Fore.RESET))
        return 1
    
    version_list = []
    version = []

    with open("C:\\Program Files\\xpykg\\db.json", 'r') as db:
        contents = loads(db.read())

        for i in list(contents.keys()):
            if is_installed(i) == True and vtoi(contents[i]['version']) > vtoi(get_installed_package_version(i)):
                version_list.append(i)
                version.append(contents[i]['version'])

    db.close()

    if len(version_list) == 0:
        print("{}{}[xpykg:info]:{} all packages are up to date".format(Style.BRIGHT, Fore.BLUE, Fore.RESET))
        return 0
    else:
        print("{}{}[xpykg:info]:{} these packages will be upgraded".format(Style.BRIGHT, Fore.BLUE, Fore.RESET))
        for i in version_list:
            print("[-] {} {}{}{} -> {}{}{}".format(i, Fore.RED, get_installed_package_version(i), Fore.RESET, Fore.GREEN, version[version_list.index(i)], Fore.RESET))

    choice = input("{}{}[xpykg:input]:{} proceed[{}y{}/{}N{}]? ".format(Style.BRIGHT, Fore.MAGENTA, Fore.RESET, Fore.GREEN, Fore.RESET, Fore.RED, Fore.RESET))
    
    if choice not in ["y", "yes", "Y"]:
        print("{}{}[xpykg:error]:{} user decided not to proceed.".format(Style.BRIGHT, Fore.RED, Fore.RESET))
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
            else:
                for i in range(2, len(argv)):
                    install_package(argv[i])
        elif argv[1] in ["-u", "uninstall", "--uninstall"]:
            if len(argv) == 3:
                uninstall_package(argv[2])
            else:
                for i in range(2, len(argv)):
                    print(argv[i])
        elif argv[1] in ["-U", "upgrade", "--upgrade"]:
            upgrade_packages()
        else:
            print("{}{}[xpykg:error]:{} invalid argument or not sufficient arguements".format(Style.BRIGHT, Fore.RED, Fore.RESET))
    except IndexError:
        print("{}{}[xpykg:error]:{} invalid argument or not sufficient arguments".format(Style.BRIGHT, Fore.RED ,Fore.RESET))
    except KeyboardInterrupt:
        print("{}{}[xpykg:error]:{} keyboard exit detected".format(Style.BRIGHT, Fore.RED, Fore.RESET))
