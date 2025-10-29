#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
    echo "run using sudo" >&2
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

cd /root/KawaiiCon-Box-CTF-2025
/usr/bin/git pull

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

echo "[*] Starting challenges"

sudo pigpiod

/usr/bin/python3 /home/raspberry/KawaiiCon-Box-CTF-2025/camera-webapp/app.py > /home/raspberry/KawaiiCon-Box-CTF-2025/webapp.log 2>&1 &
/usr/bin/python3 /home/raspberry/KawaiiCon-Box-CTF-2025/nfc-reader/card-reader.py > /home/raspberry/KawaiiCon-Box-CTF-2025/nfc.log 2>&1 &