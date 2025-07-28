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

# load variables from .env into environment
if not load_dotenv():
    print("\n\033[31m Error: .env not found or failed to load. \033[0m\n")
    sys.exit(1)

# check NAS connection
nas_ip = os.getenv("NASA_REMOTE_IP")

def ensure_nas_connection(ip):
    def can_reach_nas(ip):
        result = subprocess.run(["ping", "-n", "1", ip], capture_output=True, text=True, encoding="utf-8", errors="ignore")
        return result.returncode == 0 # 0 = ping success
    
    def connect_to_vpn():
        ovpn_gui = os.getenv("OVPN_PATH")
        ovpn_profile = os.getenv("OVPN_CONFIG")
        subprocess.run([ovpn_gui, "--command", "connect", ovpn_profile])
    
    if can_reach_nas(ip):
        return "local" # NAS in local network
    
    print("⚠️ NAS not in local network, connecting to VPN...")
    connect_to_vpn()
    time.sleep(5)

    return "vpn" if can_reach_nas(ip) else None

status = ensure_nas_connection(nas_ip)

if status == "local":
    print("✅ NAS reachable")
elif status == "vpn":
    print("✅ NAS reachable via VPN")
else:
    print("❌ NAS not reachable; VPN not working or NAS offline")
    sys.exit(1)

# connect to Raspberry Pi NAS
register_session(os.getenv("NASA_REMOTE_IP"), username=os.getenv("SMB_USERNAME"), password=os.getenv("SMB_PWD"))

# check and get paths for backup
base_path_str = os.getenv("BASE_PATH")
shared_path_str = os.getenv("SHARED_PATH")

if base_path_str is None:
    print("\n\033[31m Error: BASE_PATH environment variable is not set. \033[0m\n")
    sys.exit(1)
if shared_path_str is None:
    print("\n\033[31m Error: SHARED_PATH environment variable is not set. \033[0m\n")
    sys.exit(1)

base_path = Path(base_path_str)

if not base_path.exists():
    print(f"\n\033[31m Error: The path {base_path} does not exist. \033[0m\n")
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
        and (Path(base_path_str) / file).is_file() 
    }
    
    return list(added), list(deleted), list(modified)

def perform_monthly_backup(monthly_backup_path: Path, working_path: Path):
    pass

def perform_weekly_backup(weekly_backup_path: Path, working_path: Path):
    pass

added, deleted, modified = get_changes(Path(shared_path_str), Path(base_path_str))

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
        src = Path(base_path_str) / Path(p)
        dst_dir = Path(shared_path_str) / Path(p.parent)

        dst_dir.mkdir(parents=True, exist_ok=True)

        if src.is_file():
            shutil.copy2(src, dst_dir / p.name)

def handle_modifications(paths):
    """
    
    """
    for p in paths:
        src = Path(base_path_str) / Path(p)
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




