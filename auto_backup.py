#!/usr/bin/env python3
"""
=============================================================
  Daily Auto-Backup Script
  Runs once a day at end of shift, compresses files,
  keeps rolling backups, and logs everything.
=============================================================
"""

import os
import shutil
import zipfile
import logging
import datetime
import time
import sys
from pathlib import Path

# ─────────────────────────────────────────────
#  ★  CONFIGURE THESE SETTINGS  ★
# ─────────────────────────────────────────────

# Folders/files you want to back up (add as many as you need)
SOURCE_PATHS = [
    r"C:\Users\YourName\Documents\Work",       # Windows example
    # r"/home/yourname/documents/work",         # Mac/Linux example
    # r"D:\Projects",                           # Another folder
]

# Where backups should be saved
BACKUP_DESTINATION = r"E:\Backups"
# Examples:
#   External drive:   r"E:\Backups"
#   Network share:    r"\\server\backups\daily"
#   Mac/Linux:        r"/Volumes/BackupDrive/backups"

# Time to run the backup (24-hour format)
BACKUP_HOUR   = 22   # 17 = 5:00 PM  |  18 = 6:00 PM  |  22 = 10:00 PM
BACKUP_MINUTE = 0

# How many daily backups to keep before deleting old ones
MAX_BACKUPS_TO_KEEP = 7

# Log file location (leave blank "" to log next to this script)
LOG_FILE = ""

# ─────────────────────────────────────────────
#  Internal logic below — no need to edit
# ─────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
LOG_PATH   = Path(LOG_FILE) if LOG_FILE else SCRIPT_DIR / "backup.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AutoBackup")


def create_zip(sources: list, zip_path: Path) -> bool:
    """Zip all source paths into a single archive."""
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for src in sources:
                src = Path(src)
                if not src.exists():
                    log.warning(f"Source not found, skipping: {src}")
                    continue
                if src.is_file():
                    zf.write(src, src.name)
                    log.info(f"  + File: {src}")
                elif src.is_dir():
                    for file in src.rglob("*"):
                        if file.is_file():
                            arcname = file.relative_to(src.parent)
                            zf.write(file, arcname)
                    log.info(f"  + Folder: {src}  ({sum(1 for _ in src.rglob('*') if _.is_file())} files)")
        return True
    except Exception as e:
        log.error(f"Failed to create zip: {e}")
        return False


def prune_old_backups(dest: Path, max_keep: int):
    """Delete oldest backups if we exceed max_keep."""
    backups = sorted(dest.glob("backup_*.zip"), key=lambda f: f.stat().st_mtime)
    while len(backups) > max_keep:
        oldest = backups.pop(0)
        oldest.unlink()
        log.info(f"Deleted old backup: {oldest.name}")


def run_backup():
    """Main backup routine."""
    log.info("=" * 55)
    log.info("Starting daily backup...")

    dest = Path(BACKUP_DESTINATION)
    dest.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    zip_name  = f"backup_{timestamp}.zip"
    zip_path  = dest / zip_name

    log.info(f"Destination : {dest}")
    log.info(f"Archive     : {zip_name}")

    success = create_zip(SOURCE_PATHS, zip_path)

    if success:
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        log.info(f"Backup complete! Size: {size_mb:.2f} MB")
        prune_old_backups(dest, MAX_BACKUPS_TO_KEEP)
    else:
        log.error("Backup FAILED — check errors above.")

    log.info("=" * 55)
    return success


def seconds_until_next_run() -> float:
    """Calculate seconds until the next scheduled backup time."""
    now  = datetime.datetime.now()
    next_run = now.replace(hour=BACKUP_HOUR, minute=BACKUP_MINUTE, second=0, microsecond=0)
    if next_run <= now:
        next_run += datetime.timedelta(days=1)
    return (next_run - now).total_seconds()


def main():
    # ── CLI: run once immediately (useful for testing)
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        log.info("Manual run triggered.")
        run_backup()
        return

    log.info(f"Auto-Backup scheduler started.")
    log.info(f"Scheduled daily at {BACKUP_HOUR:02d}:{BACKUP_MINUTE:02d}")
    log.info(f"Sources   : {SOURCE_PATHS}")
    log.info(f"Destination: {BACKUP_DESTINATION}")

    while True:
        wait = seconds_until_next_run()
        next_time = (datetime.datetime.now() + datetime.timedelta(seconds=wait)).strftime("%Y-%m-%d %H:%M")
        log.info(f"Next backup scheduled for: {next_time}  (waiting {wait/3600:.1f} hrs)")
        time.sleep(wait)
        run_backup()


if __name__ == "__main__":
    main()
