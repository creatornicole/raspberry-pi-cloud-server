from datetime import datetime
from helpers import raise_env_error
from load_variables import load_variables
from pathlib import Path
import os
import shutil

def perform_backup(working_path: Path, backup_path: Path, monthly_scheduled: bool, perform_monthly_backup: bool = False):
    """
    
    """
    def find_backup_dir(dir_prefix: str) -> str:
        """
        """
        for path in backup_path.iterdir():
            if not path.is_dir():
                # skip current loop iteration and jump to the next iteration
                continue
            if path.name.startswith(dir_prefix):
                return path.name
        return None
    
    def get_backup_path(dir_prefix: str, backup_path: Path) -> Path:
        """
        """
        new_backup_dir_name = dir_prefix + datetime.today().strftime("%Y_%m_%d")
        return backup_path / new_backup_dir_name
    
    def get_changes(working_path: Path, backup_path: Path):
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
            and (working_path / file).is_file() 
        }
        
        return list(added), list(deleted), list(modified)
    
    def handle_additions(working_path: Path, backup_path: Path, paths: list[Path]):
        """
        Copies newly added files from working_path to backup_path and ensures
        that all required directory structures (including empty folders) are
        created in the backup location.
        """
        for p in paths:
            src = working_path / p
            dst = backup_path / p

            if src.is_dir():
                dst.mkdir(parents=True, exist_ok=True)
            elif src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    def handle_deletions(backup_path: Path, paths):
        """
        Removes files and directories from the backup_path that have been
        deleted from the working_path. Uses a list of relative paths to
        determine what was deleted and enures the backup is updated
        accordingly.
        """
        # identify deleted directories (= paths with no suffix)
        deleted_dirs = sorted(
            (path for path in paths if path.suffix == ""),
            # sort directories by depth (shallow first), so parent folders
            # are removed before their subdirectories - prevents errors when deleting
            key=lambda path: len(path.parts)
        )
        # identify deleted files (= paths with a suffix)
        deleted_files = list(set(paths) - set(deleted_dirs))

        # loop over deleted directories
        while deleted_dirs:
            deleted_dir = deleted_dirs.pop(0)
            # remove the directory and everything inside it from the backup
            shutil.rmtree(backup_path / Path(deleted_dir))

            # ensure that subdirectories and files inside already-deleted folders are not redundantly deleted, avoiding errors
            # filter out any subdirectories that were nested inside the just-deleted one
            deleted_dirs = [path for path in deleted_dirs if not path.is_relative_to(deleted_dir)]
            # filter out any files inside that deleted directory
            deleted_files = [path for path in deleted_files if not path.is_relative_to(deleted_dir)]

        # deleted individual files from the backup location
        for deleted_file in deleted_files:
            (backup_path / Path(deleted_file)).unlink()
    
    def handle_modifications(working_path: Path, backup_path: Path, paths):
        """
        Copies modified files from working_path to backup_path, overwriting
        the existing versions.

        Each path in 'paths' is treated as relative file path. Assumes necessary
        parent directories already exist. Preserves file metadata using shutil.copy2
        """
        for p in paths:
            src = working_path / Path(p)
            dst = backup_path / Path(p)

            # copy and overwrite existing file
            shutil.copy2(src, dst)

    success_symbol, err_symbol, warning_symbol, info_symbol = load_variables()

    prefix_env, prefix_name = ("MONTHLY_PREFIX", "monthly") if perform_monthly_backup else ("WEEKLY_PREFIX", "weekly")
    (prefix := os.getenv(prefix_env)) or raise_env_error(prefix_env)
    
    create_backup_dir = False

    curr_backup_dir = find_backup_dir(prefix)
    if not curr_backup_dir:
        create_backup_dir = True
        print(f"\033[33m{warning_symbol} {prefix_name.capitalize()} backup directory has yet to bet set up \033[0m")

    new_backup_path = get_backup_path(prefix, backup_path)

    if create_backup_dir:
        # create backup dir
        new_backup_path.mkdir(exist_ok=True)
        print(f"{info_symbol} {prefix_name.capitalize()} backup directory set up as {new_backup_path.name}")
    elif curr_backup_dir != new_backup_path.name:
        # rename backup dir
        curr_backup_path = backup_path / curr_backup_dir
        curr_backup_path.rename(new_backup_path)
        print(f"{info_symbol} {curr_backup_dir} renamed to {new_backup_path.name}")
    else:
        print(f"{info_symbol} {new_backup_path.name} already exists")

    added, deleted, modified = get_changes(working_path, new_backup_path)

    handle_additions(working_path, new_backup_path, added)
    handle_deletions(new_backup_path, deleted)
    # modification must be handled after additions and deletions,
    # because handle_modifications assumes that all required parent directories already exist
    handle_modifications(working_path, new_backup_path, modified)

    if monthly_scheduled:
        # monthly backup is scheduled, so we now trigger it by calling perform_backup again
        # we set monthly_scheduled=False to prevent recursive scheduling,
        # and perform_monhtly_backup=True to indicate that this call should actually run the monthly backup
        perform_backup(
            working_path, 
            backup_path, 
            monthly_scheduled=False, 
            perform_monthly_backup=True
        )