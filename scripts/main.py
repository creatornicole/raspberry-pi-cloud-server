# .\env\Scripts\activate

from pathlib import Path
from dotenv import load_dotenv
import os
import sys
from datetime import datetime, timedelta
from typing import Tuple
from smbclient import listdir, open_file, register_session
import subprocess
import time
import shutil
from datetime import datetime
import paho.mqtt.client as mqtt
import subprocess
import ssl
import json
import requests
from requests.auth import HTTPBasicAuth

success_symbol = "\u2705"
err_symbol = "\u274C"
warning_symbol = "\u26A0"
info_symbol = "\u2139"

# load variables from .env into environment
if not load_dotenv():
    raise EnvironmentError(f"\033[31m {err_symbol} .env not found or failed to load. \033[0m")

def connect():
    """
    """
    def is_on_same_network(target_ip: str) -> bool:
        """
        """
        result = subprocess.run(
            ["ping", "-n", "1", target_ip], 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="ignore"
        )
        return result.returncode == 0 # 0 = ping success
    
    def connect_to_vpn():
        """
        """
        ovpn_gui = os.getenv("OVPN_PATH")
        ovpn_profile = os.getenv("OVPN_CONFIG")
        if not ovpn_gui or not ovpn_profile:
            raise EnvironmentError(f"\033[31m {err_symbol} OVPN_PATH or OVPN_CONFIG environment variable not set. \033[0m")
        subprocess.run([ovpn_gui, "--command", "connect", ovpn_profile])

    def turn_on_shelly(ip):
        url = f"http://{ip}/relay/0?turn=on"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"\033[32m {success_symbol} Shelly turned ON successfully \033[0m")
            else:
                print(f"\033[31m {err_symbol} Failed to turn on Shelly. Status code: {response.status_code} \033[0m")
        except requests.RequestException as e:
            print(f"\033[31m {err_symbol} Error connecting to Shelly: {e} \033[0m")
        
    shelly_ip = os.getenv("SHELLY_IP")
    if not shelly_ip:
        raise EnvironmentError(f"\033[31m {err_symbol} SHELLY_IP environment variable is not set. \033[0m")

    if is_on_same_network(shelly_ip):
        status = "local"
    else:
        print(f"\033[33m {warning_symbol} NAS not in local network, connecting to VPN... \033[0m")
        connect_to_vpn()
        time.sleep(5)
        status = "vpn" if is_on_same_network(shelly_ip) else "unreachable"

    if status == "unreachable":
        raise RuntimeError(f"\033[31m {err_symbol} Device still unreachable after VPN connection attempt \033[0m")
    
    shelly_ip = os.getenv("SHELLY_IP")
    if not shelly_ip:
        raise EnvironmentError(f"\033[31m {err_symbol} SHELLY_IP environment variable is not set. \033[0m")
    
    turn_on_shelly(shelly_ip)
    time.sleep(20)

    # connect to Raspberry Pi NAS
    nas_ip = os.getenv("NASA_REMOTE_IP")
    if not nas_ip:
        raise EnvironmentError(f"\033[31m {err_symbol} NASA_REMOTE_IP environment variable is not set. \033[0m")
    nas_username = os.getenv("SMB_USERNAME")
    if not nas_username:
        raise EnvironmentError(f"\033[31m {err_symbol} SMB_USERNAME environment variable is not set. \033[0m")
    nas_pwd = os.getenv("SMB_PWD")
    if not nas_pwd:
        raise EnvironmentError(f"\033[31m {err_symbol} SMB_PWD environment variable is not set. \033[0m")

    register_session(os.getenv("NASA_REMOTE_IP"), username=nas_username, password=nas_pwd)

    if status == "local":
        print(f"\033[32m {success_symbol} Registered to NAS \033[0m")
    elif status == "vpn":
        print(f"\033[32m {success_symbol} Registered to NAS via VPN \033[0m")

connect()
sys.exit()

# check and get paths for backup
base_path_str = os.getenv("BASE_PATH")
shared_path_str = os.getenv("SHARED_PATH")

base_path = Path(base_path_str)
shared_path = Path(shared_path_str)

if base_path_str is None:
    print(f"\033[31m {err_symbol} BASE_PATH environment variable is not set. \033[0m")
    sys.exit(1)
if shared_path_str is None:
    print(f"\033[31m {err_symbol} SHARED_PATH environment variable is not set. \033[0m")
    sys.exit(1)


if not base_path.exists():
    print(f"\033[31m {err_symbol} The path {base_path} does not exist. \033[0m")
    sys.exit(1)

# determine whether monthly backup should be done
def is_monthly_scheduled() -> bool:
    """
    Determine whether monthly backup should be executed. If not only the weekly
    backup is done.
    """
    today = datetime.now().date()
    ddiff = 3
    
    month_changed = today.month != (today - timedelta(days=ddiff)).month
    month_changes = today.month != (today + timedelta(days=ddiff)).month

    return month_changed or month_changes

monthly = is_monthly_scheduled()

def get_changes(backup_path: Path, working_path: Path):
    """
    
    """
    backup_files = {
        f.relative_to(backup_path): f.stat().st_mtime
        for f in backup_path.rglob("*") if not f.name.startswith(".")
    }
    working_files = {
        f.relative_to(working_path): f.stat().st_mtime
        for f in working_path.rglob("*") if not f.name.startswith(".")
    }

    backup_keys = set(backup_files)
    working_keys = set(working_files.keys())

    added = working_keys - backup_keys
    deleted = backup_keys - working_keys
    modified = {
        file 
        for file in backup_keys & working_keys
        if backup_files[file] != working_files[file]
        # only consider file modications; directory modifications are ignored
        # reason 1: renaming a directory is already detected as a new and a deleted folder
        # reason 2: backed-up directories get the backup date as their modification time,
        #           which is always newer/different from the working directory even if no 
        #           actual changes were made
        and (base_path / file).is_file() 
    }
    
    return list(added), list(deleted), list(modified)

def perform_backup(backup_path: Path, working_path: Path, monthly_scheduled: bool):
    """
    
    """
    weekly_file_prefix = "automated-weekly-"
    monthly_file_prefix = "automated-monthly-"

    # find name of the current backup paths
    curr_weekly_backup_dir = None
    curr_monthly_backup_dir = None

    for path in backup_path.iterdir():
        if not path.is_dir():
            # skip current loop iteration and jump to the next iteration
            continue

        if path.name.startswith(weekly_file_prefix):
            curr_weekly_backup_dir = path.name
        elif monthly_scheduled and path.name.startswith(monthly_file_prefix):
            curr_monthly_backup_dir = path.name

    # check if directories for backup could be found
    err_msg = ""
    err_msg_weekly = f"\033[33m {warning_symbol} Weekly backup directory has yet to bet set up. \033[0m"
    err_msg_monthly = f"\033[33m {warning_symbol} Monthly backup directory has yet to bet set up. \033[0m"

    if monthly_scheduled and (curr_weekly_backup_dir is None or curr_monthly_backup_dir is None):
        errors = []
        if curr_weekly_backup_dir is None:
            errors.append(err_msg_weekly)
        if curr_monthly_backup_dir is None:
            errors.append(err_msg_monthly)
        err_msg = "\n".join(errors)
    elif curr_weekly_backup_dir is None:
        err_msg = err_msg_weekly

    # new name of the backup paths
    new_weekly_backup_dir = weekly_file_prefix + datetime.today().strftime("%Y_%m_%d")
    new_monthly_backup_dir = monthly_file_prefix + datetime.today().strftime("%Y_%m_%d")

    new_weekly_backup_path = shared_path / new_weekly_backup_dir
    new_monthly_backup_path = shared_path / new_monthly_backup_dir

    # check if backup directories have to be created or renamed
    if err_msg:
        print(err_msg)
    
    # TODO: create own function with that?
    if err_msg_weekly in err_msg:
        new_weekly_backup_path.mkdir(exist_ok=True)
        print(f"{info_symbol} Weekly backup directory set up as {new_weekly_backup_dir}")
    elif curr_weekly_backup_dir != new_weekly_backup_dir:
        curr_weekly_backup_path = shared_path / curr_weekly_backup_dir
        curr_weekly_backup_path.rename(new_weekly_backup_path)
        print(f"{info_symbol} {curr_weekly_backup_dir} renamed to {new_weekly_backup_dir}")
        
    if err_msg_monthly in err_msg:
        new_monthly_backup_path.mkdir(exist_ok=True)
        print(f"{info_symbol} Monthly backup directory set up as {new_monthly_backup_dir}")
    elif monthly_scheduled and curr_monthly_backup_dir != new_monthly_backup_dir:
        curr_monthly_backup_path = shared_path / curr_monthly_backup_dir
        curr_monthly_backup_path.rename(new_monthly_backup_path)
        print(f"{info_symbol} {curr_monthly_backup_dir} renamed to {new_monthly_backup_dir}")

    sys.exit()

perform_backup(Path(shared_path_str), base_path, True)

def perform_monthly_backup(monthly_backup_path: Path, working_path: Path):

    pass

def perform_weekly_backup(weekly_backup_path: Path, working_path: Path):
    pass

added, deleted, modified = get_changes(Path(shared_path_str), base_path)

def handle_deletions(paths):
    """
    
    """
    # get deleted directories 
    deleted_dirs = sorted(
        (path for path in paths if path.suffix == ""), # only paths with no suffix = directories
        key=lambda path: len(path.parts) # sort by number of parts to remove directories before subdirectories
    )
    deleted_files = list(set(paths) - set(deleted_dirs))

    # remove the deleted directories with all of their content
    while deleted_dirs:
        deleted_dir = deleted_dirs.pop(0) # remove and return first element

        # delete directory with all of its files and subdirectories
        shutil.rmtree(Path(shared_path_str) / Path(deleted_dir))

        # update set (remove all subdirectories from deleted_dirs list)
        deleted_dirs = [path for path in deleted_dirs if not path.is_relative_to(deleted_dir)]
        # remove all files from deleted_files list that were inside the deleted_dir
        deleted_files = [path for path in deleted_files if not path.is_relative_to(deleted_dir)]

    # remove the deleted files
    for deleted_file in deleted_files:
        (Path(shared_path_str) / Path(deleted_file)).unlink()    

def handle_additions(paths):
    """
    Copies newly added files and ensures that all required directories (including empty ones)
    are created in the target location.
    """
    for p in paths:
        src = base_path / Path(p)
        dst_dir = Path(shared_path_str) / Path(p.parent)

        dst_dir.mkdir(parents=True, exist_ok=True)

        if src.is_file():
            shutil.copy2(src, dst_dir / p.name)

def handle_modifications(paths):
    """
    
    """
    for p in paths:
        src = base_path / Path(p)
        dst = Path(shared_path_str) / Path(p)

        # copy and overwrite existing file
        shutil.copy2(src, dst)

handle_deletions(deleted)
handle_additions(added)
handle_modifications(modified)

sys.exit()

monthly = False
curr_week = datetime.now().isocalendar().week
print(curr_week)

if monthly:
    monthly_backup_path = os.getenv()

weekly_backup_path = os.getenv()

# find all files from the base path directory (ignore hidden files and directories)
files = [f for f in base_path.glob("*") if not f.name.startswith(".")]
# sort by modification time, descending (most recent first)
files_sorted = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

for f in files_sorted:
    mod_time = datetime.fromtimestamp(f.stat().st_mtime)
    formatted_time = mod_time.strftime("%d.%m.%Y %H:%M:%S")
    print(formatted_time, f)

#### TODO:
# shut off pi
# ...
# disconnect from VPN
# close the session
# ...




