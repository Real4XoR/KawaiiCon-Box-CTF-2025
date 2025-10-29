#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
    echo "run using sudo" >&2
    exit 1
fi

# ===== Configuration =====

DB="/home/home/raspberry/KawaiiCon-Box-CTF-2025/user.db"
USERNAME="admin"
RANDOM_LENGTH=24
RANDOM_STRING=$(< /dev/urandom tr -dc 'A-Za-z0-9' | head -c "$RANDOM_LENGTH")
HASH=$(echo -n "$RANDOM_STRING" | md5sum | awk '{print $1}')

# ===== Update Backup =====

echo "[*] Checking for updates in backup"

cd /root/KawaiiCon-Box-CTF-2025
/usr/bin/git pull

# ===== Overwrite Files =====

echo "[*] Overwriting with backup"

/usr/bin/cp /root/KawaiiCon-Box-CTF-2025 /home/home/raspberry/KawaiiCon-Box-CTF-2025

# ===== Generate Admin Hash =====

echo "[*] Generating user.db" 

sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS USERS(
  USERNAME TEXT PRIMARY KEY NOT NULL,
  PASSWORD TEXT NOT NULL
); INSERT OR REPLACE INTO USERS (USERNAME, PASSWORD) VALUES ('$USERNAME', '$HASH');"

echo "[*] Webapp admin password: $RANDOM_STRING"
echo "$RANDOM_STRING" > /root/webapp_admin_password.txt

# ===== Run Challenges =====

echo "[*] Starting challenges"

/usr/bin/python3 /home/raspberry/KawaiiCon-Box-CTF-2025/camera-webapp/app.py && echo "[*] Webapp challenge started"
/usr/bin/python3 /home/raspberry/KawaiiCon-Box-CTF-2025/nfc-reader/card-reader.py && echo "[*] NFC challenge started"