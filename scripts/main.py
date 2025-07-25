from pathlib import Path
from dotenv import load_dotenv
import os
import sys
from datetime import datetime, timedelta
from typing import Tuple
from smbclient import listdir, open_file, register_session

# load variables from .env into environment
if not load_dotenv():
    print("\n\033[31m Error: .env not found or failed to load. \033[0m\n")
    sys.exit(1)

# enable VPN
# TODO: only if needed
ovpn_config_str = os.getenv("OVPN_CONFIG")


sys.exit()

# connect to Raspberry Pi NAS
register_session(os.getenv("NASA_REMOTE_IP"), username=os.getenv("SMB_USERNAME"), password=os.getenv("SMB_PWD"))

# check defined paths
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

def get_changes(backup_path: Path, working_path: Path) -> Tuple[str, str, str]:
    """
    
    """
    backup_files = {
        f.relative_to(backup_path): f.stat().st_mtime
        for f in backup_path.glob("*") if not f.name.startswith(".")
    }
    working_files = {
        f.relative_to(working_path): f.stat().st_mtime
        for f in working_path.glob("*") if not f.name.startswith(".")
    }

    backup_keys = set(backup_files)
    working_keys = set(working_files.keys())

    added = working_keys - backup_keys
    deleted = backup_keys - working_keys
    modified = {
        file for file in backup_keys & working_keys
        if backup_files[file] != working_files[file]
    }
    
    return added, deleted, modified

def perform_monthly_backup(monthly_backup_path: Path, working_path: Path):
    pass

def perform_weekly_backup(weekly_backup_path: Path, working_path: Path):
    pass

added, deleted, modified = get_changes(Path(r"C:\Users\ngott\Code\raspberry-pi-cloud-server\old"), Path(r"C:\Users\ngott\Code\raspberry-pi-cloud-server\new"))

# list content in shared folder
for filename in listdir(shared_path_str):
    print(filename)


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




