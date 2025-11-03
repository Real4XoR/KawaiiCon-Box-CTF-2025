#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
    echo "Run using sudo" >&2
    exit 1
fi

# ===== Configuration =====

DB="/home/raspberry/KawaiiCon-Box-CTF-2025/camera-webapp/static/user.db"
USERNAME="admin"
RANDOM_LENGTH=24
PASSWORD_STRING=$(< /dev/urandom tr -dc 'A-Za-z0-9' | head -c "$RANDOM_LENGTH")
SESSION_STRING=$(< /dev/urandom tr -dc 'A-Za-z0-9' | head -c "$RANDOM_LENGTH")
HASH=$(echo -n "$PASSWORD_STRING" | md5sum | awk '{print $1}')

# ===== Update Backup =====

echo "[*] Checking for updates in backup"

cd /home/raspberry/KawaiiCon-Box-CTF-2025

# ===== Kill Existing Processes

while true; do
    read -p "Have you stopped the running challenges? [y/n]: " yn
    case $yn in
        [Yy]* )
            if [ -f app.pid ]; then
                echo "[*] Removing existing app.pid"
                rm app.pid
            else
                echo "[*] No app.pid file found. Continuing"
            fi
            break
            ;;
        [Nn]* )
            if [ -f app.pid ]; then
                echo "Run: sudo kill \$(cat app.pid)"
            else
                echo "[*] No app.pid file found, nothing to kill."
            fi
            exit 1
            ;;
        * )
            echo "Please answer y (yes) or n (no)."
            ;;
    esac
done

# ===== Overwrite Files =====

echo "[*] Overwriting with backup"

/usr/bin/cp -r /root/KawaiiCon-Box-CTF-2025 /home/raspberry

# ===== Generate Admin Hash =====

echo "[*] Generating random admin password" 

rm $DB

sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS USERS(
  USERNAME TEXT PRIMARY KEY NOT NULL,
  PASSWORD TEXT NOT NULL,
  SESSION TEXT NOT NULL
); INSERT OR REPLACE INTO USERS (USERNAME, PASSWORD, SESSION) VALUES ('$USERNAME', '$HASH', '$SESSION_STRING');"

echo "[*] Webapp admin password: $PASSWORD_STRING"
echo "$PASSWORD_STRING" > /root/webapp_admin_password.txt

# ===== Run Challenges =====

if pgrep -x "pigpiod" >/dev/null; then
    echo "[*] Pigpiod is already running, skipping"
else
    sudo pigpiod
    echo "[*] Starting Pigpiod"
fi

if [ -f *.log ]; then
    echo "[*] Removing existing log file"
    rm *.log
else
    echo "[*] No log file found. Continuing"
fi

echo "[*] Starting challenges"

/usr/bin/python3 camera-webapp/app.py > webapp.log 2>&1 &
echo $! > app.pid
/usr/bin/python3 nfc-reader/card-reader.py
echo $! >> app.pid
