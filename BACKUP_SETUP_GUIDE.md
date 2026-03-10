# Daily Auto-Backup — Setup Guide

## 1. Requirements
- **Python 3.7+** — Download from https://python.org if not installed
- No extra libraries needed (uses only Python built-ins)

---

## 2. Configure the Script

Open `auto_backup.py` in any text editor and update the top section:

```python
SOURCE_PATHS = [
    r"C:\Users\YourName\Documents\Work",   # ← Your folder(s) to back up
]

BACKUP_DESTINATION = r"E:\Backups"         # ← Where to save backups

BACKUP_HOUR   = 17   # ← 17 = 5:00 PM end of shift
BACKUP_MINUTE = 0

MAX_BACKUPS_TO_KEEP = 7   # ← Keep last 7 days, auto-delete older ones
```

---

## 3. Test It Manually

Run this in your terminal to do an **immediate test backup**:

```bash
python auto_backup.py --now
```

Check the `backup.log` file next to the script to confirm it worked.

---

## 4. Schedule It to Run Automatically

### ✅ Windows — Task Scheduler

1. Open **Task Scheduler** (search in Start menu)
2. Click **"Create Basic Task"**
3. Name: `Daily End-of-Shift Backup`
4. Trigger: **Daily** → set time to `5:00 PM`
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `"C:\path\to\auto_backup.py"`
6. Click Finish ✓

> **Tip:** In Task Scheduler → Properties → Settings, check  
> *"Run task as soon as possible after a scheduled start is missed"*  
> so it catches up if the PC was off.

---

### ✅ Mac — cron (Terminal)

Open Terminal and run:

```bash
crontab -e
```

Add this line (runs at 5:00 PM every day):

```
0 17 * * * /usr/bin/python3 /Users/yourname/auto_backup.py >> /Users/yourname/backup_cron.log 2>&1
```

Save and exit. Verify with `crontab -l`.

---

### ✅ Linux — cron or systemd

**cron (same as Mac above)**

Or use a **systemd timer** for more control — ask for a systemd template if needed.

---

## 5. What the Script Does Each Run

| Step | What Happens |
|------|-------------|
| 1 | Scans all SOURCE_PATHS |
| 2 | Compresses everything into `backup_YYYY-MM-DD_HH-MM.zip` |
| 3 | Saves zip to BACKUP_DESTINATION |
| 4 | Deletes oldest backup if more than MAX_BACKUPS_TO_KEEP exist |
| 5 | Logs result to `backup.log` |

---

## 6. Backup File Naming

Each backup is named with a timestamp so you always know when it was made:

```
backup_2026-03-10_17-00.zip
backup_2026-03-11_17-00.zip
backup_2026-03-12_17-00.zip
...
```

---

## 7. Troubleshooting

| Problem | Fix |
|---------|-----|
| "Source not found" warning | Check SOURCE_PATHS spelling |
| Backup destination not created | Check you have write permission to the folder |
| Script runs but no zip appears | Look at `backup.log` for error details |
| Task Scheduler doesn't trigger | Make sure PC is on; check Task Scheduler history tab |

---

## 8. Customization Tips

- **Multiple folders:** Add more lines to `SOURCE_PATHS`
- **Network drive:** Use `\\\\server\\share\\folder` on Windows
- **Different time:** Change `BACKUP_HOUR` (24h format)
- **Keep more backups:** Increase `MAX_BACKUPS_TO_KEEP`
- **Email notification:** Ask for an enhanced version with email alerts
