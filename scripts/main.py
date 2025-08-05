# .\env\Scripts\activate

from connect import connect
from datetime import datetime, timedelta
from disconnect import disconnect
from dotenv import load_dotenv
from load_variables import load_variables
from pathlib import Path
from perform_backup import perform_backup
import os
import time

success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

# load variables from .env into environment
if not load_dotenv():
    raise EnvironmentError(f"\033[31m{err_symbol} .env not found or failed to load \033[0m")

# connect to the Raspberry Pi NAS
connect()

# prepare for backup
working_path_str = os.getenv("WORKING_PATH")
if not working_path_str:
    raise EnvironmentError(f"\033[31m{err_symbol} WORKING_PATH environment variable is not set \033[0m")
backup_path_str = os.getenv("BACKUP_PATH")
if not backup_path_str:
    raise EnvironmentError(f"\033[31m{err_symbol} BACKUP_PATH environment variable is not set \033[0m")

working_path = Path(working_path_str)
if not working_path.exists():
    raise FileNotFoundError(f"\033[31m{err_symbol} Invalid path {working_path_str} \033[0m")
backup_path = Path(backup_path_str)
if not backup_path.exists():
    raise FileNotFoundError(f"\033[31m{err_symbol} Invalid path {backup_path_str} \033[0m")

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

perform_backup(working_path, backup_path, is_monthly_scheduled())
time.sleep(15)

disconnect()




