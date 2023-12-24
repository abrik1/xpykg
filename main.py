"""
xpykg: manage software packages on Windows XP
"""

from ast import literal_eval
from json import loads
from os import chdir, getenv, mkdir, system
from os.path import isdir, isfile
from sys import argv, exit

from colorama import Fore, Style, init
from requests import get
from requests.exceptions import ConnectionError, ConnectTimeout, MissingSchema

try:
    from wmi import WMI
except Exception:
    print(
        "{}{}[xpykg:error]:{} unable to initialize {}WMI{}".format(
            Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, Fore.RESET
        )
    )
    exit(1)
from platform import architecture
from time import sleep

xpykg_version = "0.1"  # xpykg version
init()  # colorama
wmi = WMI()  # wmi


def sync_database():
    """
    sync_database(): downloads database from github and dumps to Program Files
    """
    if isfile("C:\\Program Files\\xpykg\\db.json") == False:
        if isdir("C:\\Program Files\\xpykg") == False:
            mkdir("C:\\Program Files\\xpykg")

        print(
            "{}{}[xpykg:info]{}: downloading database".format(
                Style.BRIGHT, Fore.BLUE, Fore.RESET
            )
        )
        with open("C:\\Program Files\\xpykg\\db.json", "w") as xpykg_db:
            try:
                info = get("https://codeberg.org/abrik1/xpykg/raw/branch/main/db.json")
                xpykg_db.write(info.content.decode("utf-8"))
                xpykg_db.close()
                return 0
            except (
                MissingSchema,
                ConnectionError,
                ConnectionAbortedError,
                ConnectTimeout,
                ConnectionRefusedError,
                ConnectionResetError,
            ):
                print(
                    "{}{}[xpykg:error]{}: database failed to download... please try again later".format(
                        Style.BRIGHT, Fore.RED, Fore.RESET
                    )
                )
                xpykg_db.close()
                return 1
        print(
            "{}{}[xpykg:success]:{} database written".format(
                Style.BRIGHT, Fore.GREEN, Fore.RESET
            )
        )
        return 0
    else:
        with open("C:\\Program Files\\xpykg\\db.json", "r+") as xpykg_db:
            try:
                info = get("https://codeberg.org/abrik1/xpykg/raw/branch/main/db.json")
                if xpykg_db.read() == info.content.decode("utf-8"):
                    print(
                        "{}{}[xpykg:note]:{} database up to date".format(
                            Style.BRIGHT, Fore.BLUE, Fore.RESET
                        )
                    )
                    xpykg_db.close()
                    return 0
                else:
                    xpykg_db.seek(0)
                    xpykg_db.write(info.content.decode("utf-8"))
                    xpykg_db.truncate()
                    xpykg_db.close()
                    print(
                        "{}{}[xpykg:success]:{} database updated".format(
                            Style.BRIGHT, Fore.GREEN, Fore.RESET
                        )
                    )
                    return 0
            except (
                MissingSchema,
                ConnectionError,
                ConnectionAbortedError,
                ConnectTimeout,
                ConnectionRefusedError,
                ConnectionResetError,
            ):
                print(
                    "{}{}[xpykg:error]:{} database failed to download... please try again later".format(
                        Style.BRIGHT, Fore.RED, Fore.RESET
                    )
                )
                xpykg_db.close()
                return 1


def list_packages():
    """
    list_packages(): shows the list of packages
    """
    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", "r") as db:
            contents = loads(db.read())
            for i in list(contents.keys()):
                if is_installed(i) == True:
                    print(
                        "{} {} [installed by xpykg]".format(i, contents[i]["version"])
                    )
                else:
                    print("{} {}".format(i, contents[i]["version"]))
        db.close()
    else:
        print("[xpykg:error]: package index not found... please sync the database")


def search_packages(query: str):
    """
    search_packages(query: str): search packages that match a query
    """

    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", "r") as db:
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
                        print(
                            "{} {} [installed by xpykg]".format(
                                i, contents[i]["version"]
                            )
                        )
                    else:
                        print("{} {}".format(i, contents[i]["version"]))

            if count == 0:
                print(
                    "{}{}[xpykg:error]:{} no pkgs similar to {}{}{}".format(
                        Style.BRIGHT,
                        Fore.RED,
                        Fore.RESET,
                        Fore.YELLOW,
                        query,
                        Fore.RESET,
                    )
                )
        db.close()
    else:
        print(
            "{}{}[xpykg:error]:{} database not found... please sync the database".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )


def install_package(package: str):
    """
    install_package(package): install package to
    """

    if is_installed(package) == True:
        print(
            "{}{}[xpykg:input]:{} package {}{}{} is installed.. reinstall[{}y{}/{}N{}]? ".format(
                Style.BRIGHT,
                Fore.MAGENTA,
                Fore.RESET,
                Fore.YELLOW,
                package,
                Fore.RESET,
                Fore.GREEN,
                Fore.RESET,
                Fore.RED,
                Fore.RESET,
            ),
            end="",
        )
        yn = input()
        if yn in ["N", "n", "no", "NO"]:
            print(
                "{}{}[xpykg:note]:{} package {}{}{} is already installed".format(
                    Style.BRIGHT,
                    Fore.BLUE,
                    Fore.RESET,
                    Fore.YELLOW,
                    package,
                    Fore.RESET,
                )
            )
            return 0
        else:
            if uninstall_package(package) == 0:
                pass
            else:
                print(
                    "{}{}[xpykg:error]:{} package {}{}{} not reinstalled".format(
                        Style.BRIGHT,
                        Fore.RED,
                        Fore.RESET,
                        Fore.YELLOW,
                        package,
                        Fore.RESET,
                    )
                )
                return 1

    if isfile("C:\\Program Files\\xpykg\\db.json") == True:
        with open("C:\\Program Files\\xpykg\\db.json", "r") as db:
            contents = loads(db.read())

            if package not in list(contents.keys()):
                print(
                    "{}{}[xpykg:error]:{} package {}{}{} not found in database... sync the database or search for a similar package".format(
                        Style.BRIGHT,
                        Fore.RED,
                        Fore.RESET,
                        Fore.YELLOW,
                        package,
                        Fore.RESET,
                    )
                )
                db.close()
                return 1

            print(
                "{}{}[xpykg:info]:{} downloading setup.exe for package {}{}{}".format(
                    Style.BRIGHT,
                    Fore.BLUE,
                    Fore.RESET,
                    Fore.YELLOW,
                    package,
                    Fore.RESET,
                )
            )

            try:
                exe_contents = get(contents[package]["source"])
            except (
                MissingSchema,
                ConnectionError,
                ConnectionAbortedError,
                ConnectTimeout,
                ConnectionRefusedError,
                ConnectionResetError,
            ):
                print(
                    "{}{}[xpykg:error]:{} setup.exe for package {}{}{} failed to download... please try again later".format(
                        Style.BRIGHT,
                        Fore.RED,
                        Fore.RESET,
                        Fore.YELLOW,
                        package,
                        Fore.RESET,
                    )
                )
                return 1

            # Windows executables can either be in .exe or in .msi
            # the code below determines the source file is an .exe or a .msi and saves according to it

            status_code = 0  # system() will take over this variable

            print(
                "{}{}[xpykg:note]:{} running installer for package {}{}{}".format(
                    Style.BRIGHT,
                    Fore.BLUE,
                    Fore.RESET,
                    Fore.YELLOW,
                    package,
                    Fore.RESET,
                )
            )

            if "installNotes" in list(contents[package]).keys():
                print(
                    "{}{}[xpykg:notes before install]:{} {}".format(
                        Style.BRIGHT,
                        Fore.MAGENTA,
                        Fore.RESET,
                        contents[package]["installNotes"],
                    )
                )

            if (
                contents[package]["source"].split(".")[
                    len(contents[package]["source"].split(".")) - 1
                ]
                == "exe"
            ):
                with open("{}\\setup.exe".format(getenv("Temp")), "wb") as setup:
                    setup.write(exe_contents.content)
                setup.close()
                status_code = system("{}\\setup.exe".format(getenv("Temp")))

            elif (
                contents[package]["source"].split(".")[
                    len(contents[package].split(".")) - 1
                ]
                == "msi"
            ):
                with open("{}\\setup.msi".format(getenv("Temp")), "wb") as setup:
                    setup.write(exe_contents.content)
                setup.close()

                status_code = system(
                    "{}\\setup.msi".format(getenv("Temp"))
                )  # 0 for good exit.
    else:
        print(
            "{}{}[xpykg:error]:{} package index not found... maybe sync the database".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )

        # now append to install and categorize uninstallers as normal, nullsoft or custom

    if status_code == 0:
        print(
            "{}{}[xpykg:success]:{} {}{}{} installed successfully".format(
                Style.BRIGHT, Fore.GREEN, Fore.RESET, Fore.YELLOW, package, Fore.RESET
            )
        )
        if "nullsoftUninstaller" in list(
            contents[package].keys()
        ):  # determine nullsoft uninstallers:
            if architecture()[0] == "64bit" and "packagehas64" not in list(
                contents[package].keys()
            ):
                append_to_install(
                    package,
                    contents[package]["version"],
                    contents[package]["remover"].replace(
                        "Program Files", "Program Files (x86)"
                    ),
                    "nullsoftUninstaller",
                )
            else:
                append_to_install(
                    package,
                    contents[package]["version"],
                    contents[package]["remover"],
                    "nullsoftUninstaller",
                )
        else:  # for normal uninstallers
            if architecture()[0] == "64bit" and "packagehas64" not in list(
                contents[package].keys()
            ):
                append_to_install(
                    package,
                    contents[package]["version"],
                    contents[package]["remover"].replace(
                        "Program Files", "Program Files (x86)"
                    ),
                    "Normal",
                )
            else:
                append_to_install(
                    package,
                    contents[package]["version"],
                    contents[package]["remover"],
                    "Normal",
                )

        if "packagerNotes" in list(contents[package].keys()):  # notes by the packager:
            print(
                "{}{}[xpykg:packager notes]:{} {}".format(
                    Style.BRIGHT,
                    Fore.MAGENTA,
                    Fore.RESET,
                    contents[package]["packagerNotes"],
                )
            )

        return 0
    else:
        print(
            "{}{}[xpykg:error]: {}{} failed to install".format(
                Style.BRIGHT, Fore.RED, Fore.YELLOW, Fore.RESET
            )
        )
        return 1


def append_to_install(pkgname: str, version: str, remover: str, uninstall_type: str):
    """
    append_to_install(pkgname, version, remover): append package to install database
    """
    if isfile("C:\\Program Files\\xpykg\\installed-packages") == False:
        with open("C:\\Program Files\\xpykg\\installed-packages", "w") as db:
            db.write("{}".format([pkgname, version, remover, uninstall_type]))
        db.close()
    else:
        with open("C:\\Program Files\\xpykg\\installed-packages", "a+") as db:
            db.write("\n{}".format([pkgname, version, remover, uninstall_type]))
        db.close()


def is_installed(pkgname: str):
    """
    is_installed(pkgname) -> True/False
    determines whether a package is installed
    """
    if isfile("C:\\Program Files\\xpykg\\installed-packages") == True:
        with open("C:\\Program Files\\xpykg\\installed-packages", "r") as database:
            contents = database.read()
            for i in contents.splitlines():
                try:
                    if literal_eval(i)[0] == pkgname:
                        database.close()
                        return True
                except SyntaxError:
                    continue

        database.close()
        return False
    else:
        return False


def get_installed_package_version(pkgname: str):
    """
    get_installed_package_version(pkgname)
    if pkgname is installed by xpykg, return its version
    """

    if is_installed(pkgname) == True:
        with open("C:\\Program Files\\xpykg\\installed-packages", "r") as database:
            contents = database.read().splitlines()
            for i in contents:
                if literal_eval(i)[0] == pkgname:
                    database.close()
                    return literal_eval(i)[1]  # good output
    else:
        return 1  # bad output


def arr_to_str(arr, optchar: str):
    nstr = ""
    for i in arr:
        nstr = nstr + i + optchar

    return nstr


def uninstall_package(pkgname: str):
    """
    uninstall_package(pkgname): remove pkgname if installed by xpykg
    """
    if is_installed(pkgname) == True:
        with open("C:\\Program Files\\xpykg\\installed-packages", "r+") as ipkg:
            contents = ipkg.read().splitlines()
            index = 0
            remover = ""
            uninstall_type = ""
            for i in contents:
                try:
                    if literal_eval(i)[0] == pkgname:
                        index = contents.index(i)
                        remover = literal_eval(i)[2]
                        uninstall_type = literal_eval(i)[3]
                        break
                except SyntaxError:
                    continue

            remove = remover.split("\\")
            remove.pop(len(remove) - 1)
            chdir(arr_to_str(remove, "\\"))

            remover = remover.split("\\")[len(remover.split("\\")) - 1]

            print(
                "{}{}[xpykg:note]:{} loading remover for package {}{}{}".format(
                    Style.BRIGHT,
                    Fore.BLUE,
                    Fore.RESET,
                    Fore.YELLOW,
                    pkgname,
                    Fore.RESET,
                )
            )
            remove_status = system(remover)
            pkg_removed = False

            if remove_status == 0 and uninstall_type == "Normal":
                pkg_removed = True
            elif remove_status == 0 and uninstall_type == "nullsoftUninstaller":
                # using wmi check that Un_A.exe is running or not
                sleep(5)
                bin = ""
                while True:
                    prcs = []  # array to store processes running
                    for process in wmi.Win32_Process():
                        prcs.append(process.Name)

                    if "Un_A.exe" in prcs:
                        bin = "Un_A.exe"
                    elif "Au_.exe" in prcs:
                        bin = "Au_.exe"
                    elif (
                        "Uninst.exe" in prcs
                    ):  # 7zip has a very similar uninstller to NSIS Installers.
                        bin = "Uninst.exe"

                    if (bin in prcs) == False:
                        break  # assumption that it has been uninstalled..

                if isfile(remover) == True:
                    pkg_removed = False
                else:
                    pkg_removed = True
            else:
                print(
                    "{}{}[xpykg:error]:{} {}{}{} not removed".format(
                        Style.BRIGHT,
                        Fore.RED,
                        Fore.RESET,
                        Fore.YELLOW,
                        pkgname,
                        Fore.RESET,
                    )
                )
                ipkg.close()
                return 1

            if pkg_removed == False:
                print(
                    "{}{}[xpykg:error]: {}{}{} not removed".format(
                        Style.BRIGHT, Fore.RED, Fore.YELLOW, pkgname, Fore.RESET
                    )
                )
                return 1
            else:
                print(
                    "{}{}[xpykg:success]: {}{}{} removed".format(
                        Style.BRIGHT, Fore.GREEN, Fore.YELLOW, pkgname, Fore.RESET
                    )
                )
                contents.pop(index)
                ncontent = ""
                for j in contents:
                    ncontent = ncontent + j + "\n"

                ipkg.seek(0)
                ipkg.write(ncontent)
                ipkg.truncate()
                ipkg.close()
                return 0
    else:
        print(
            "{}{}[xpykg:error]:{} package {}{}{} not installed".format(
                Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, pkgname, Fore.RESET
            )
        )
        return 1


def vtoi(version: str):
    """
    vtoi(version): convert a version to an integer... 22.10 -> 2210
    """

    ver = ""

    for i in version:
        try:
            ver = ver + str(int(i))
        except ValueError:
            continue

    return int(ver)


def upgrade_packages():
    """
    upgrade_packages(): this function is the main upgrade function for xpykg
    """
    print(
        "{}{}[xpykg:note]:{} updating database".format(
            Style.BRIGHT, Fore.BLUE, Fore.RESET
        )
    )

    if sync_database() != 0:
        print(
            "{}{}[xpykg:error]:{} database failed to sync".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )
        return 1

    version_list = []
    version = []

    with open("C:\\Program Files\\xpykg\\db.json", "r") as db:
        contents = loads(db.read())

        for i in list(contents.keys()):
            try:
                if is_installed(i) == True and vtoi(contents[i]["version"]) > vtoi(
                    get_installed_package_version(i)
                ):
                    version_list.append(i)
                    version.append(contents[i]["version"])
            except SyntaxError:
                continue

    db.close()

    if len(version_list) == 0:
        print(
            "{}{}[xpykg:info]:{} all packages are up to date".format(
                Style.BRIGHT, Fore.BLUE, Fore.RESET
            )
        )
        return 0
    else:
        print(
            "{}{}[xpykg:info]: {}{}{} packages to be upgraded".format(
                Style.BRIGHT, Fore.BLUE, Fore.YELLOW, len(version), Fore.RESET
            )
        )
        for i in version_list:
            print(
                "[{}] {} {}{}{} -> {}{}{}".format(
                    version_list.index(i) + 1,
                    i,
                    Fore.RED,
                    get_installed_package_version(i),
                    Fore.RESET,
                    Fore.GREEN,
                    version[version_list.index(i)],
                    Fore.RESET,
                )
            )

    print(
        "{}{}[xpykg:input]:{} proceed[{}y{}/{}N{}]? ".format(
            Style.BRIGHT,
            Fore.MAGENTA,
            Fore.RESET,
            Fore.GREEN,
            Fore.RESET,
            Fore.RED,
            Fore.RESET,
        ),
        end="",
    )
    choice = input()
    failed_packages = []

    if choice not in ["y", "yes", "Y"]:
        print(
            "{}{}[xpykg:error]:{} user decided not to proceed.".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )
        return 1

    for i in version_list:
        print(
            "{}{}[xpykg:info]: {}{}{}/{}{}{} removing old version and installing new version of package {}{}{}".format(
                Style.BRIGHT,
                Fore.BLUE,
                Fore.YELLOW,
                version_list.index(i) + 1,
                Fore.RESET,
                Fore.YELLOW,
                len(version_list),
                Fore.RESET,
                Fore.YELLOW,
                i,
                Fore.RESET,
            )
        )
        if uninstall_package(i) == 0:
            if install_package(i) == 0:
                continue
            else:
                print(
                    "{}{}[xpykg:error]:{} package {}{}{} failed to upgrade".format(
                        Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, i, Fore.RESET
                    )
                )
                failed_packages.append(i)
        else:
            print(
                "{}{}[xpykg:error]:{} package {}{}{} failed to upgrade".format(
                    Style.BRIGHT, Fore.RED, Fore.RESET, Fore.YELLOW, i, Fore.RESET
                )
            )
            failed_packages.append(i)

    if len(failed_packages) == 0:
        print(
            "{}{}[xpykg:success]:{} all packages were upgraded sucessfully".format(
                Style.BRIGHT, Fore.GREEN, Fore.RESET
            )
        )
    else:
        with open("C:\\Program Files\\xpykg\\pkgs_failed_to_upgrade", "w") as file:
            file.write(str(failed_packages))
            file.close()

        print(
            "{}{}[xpykg:error]:{} some packages failed to upgrade".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )
        return 1


if __name__ == "__main__":
    try:
        if argv[1] in ["-h", "help", "--help"]:
            print(
                """xpykg: a script for software management for Windows XP
=====================================================
help: view this page
install: install <pkg>
list: show all the available apps
search: search <pkg>
sync: sync software databases
uninstall: uninstall <pkg>
upgrade: upgrade packages installed using xpykg
version: show xpykg version"""
            )
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
                    uninstall_package(argv[i])
        elif argv[1] in ["-U", "upgrade", "--upgrade"]:
            upgrade_packages()
        else:
            print(
                "{}{}[xpykg:error]:{} invalid argument or not sufficient arguements".format(
                    Style.BRIGHT, Fore.RED, Fore.RESET
                )
            )
            exit(1)
    except IndexError:
        print(
            "{}{}[xpykg:error]:{} invalid argument or not sufficient arguments".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )
        exit(1)
    except KeyboardInterrupt:
        print(
            "{}{}[xpykg:error]:{} keyboard exit detected".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )
        exit(1)
    except PermissionError:
        print(
            "{}{}[xpykg:error]:{} please run xpykg as Administrator".format(
                Style.BRIGHT, Fore.RED, Fore.RESET
            )
        )
        exit(1)
