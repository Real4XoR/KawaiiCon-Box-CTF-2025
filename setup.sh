#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
    echo "run as root" >&2
    exit 1
fi

# ===== Configuration =====

USER="raspberry" 
HOME_DIR="/home/$USER"
SSH_DIR="$HOME_DIR/.ssh"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"

SSID="BlackBoxZero"
PASSWORD="whothoughtofthisshittypassword"

PUBLIC_KEYS=(
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDpj9EFTdCIGm60Im6ZltQZ53kEIJ7YiUwfpBVmnFCjJ ncobbald@Laptops-MacBook-Pro.local"
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE5HKN7vqMDm2aEAN63mgjhN/bGha9kdHEqDqEawz+YI bskerman@C02C204LJHD3s-MacBook-Pro.local"
)

echo "===== BlackBoxZero Setup Starting ====="

# ===== SSH Configuration =====

echo ">>> Configuring SSH access and keys"

sudo mkdir -p "$SSH_DIR"
sudo chmod 700 "$SSH_DIR"
sudo touch "$AUTHORIZED_KEYS"
sudo chmod 600 "$AUTHORIZED_KEYS"

for key in "${PUBLIC_KEYS[@]}"; do
    if ! grep -q "$key" "$AUTHORIZED_KEYS"; then
        echo "$key" | sudo tee -a "$AUTHORIZED_KEYS" >/dev/null
        echo "Added key: ${key:0:40}..."
    fi
done

sudo chown -R "$USER:$USER" "$SSH_DIR"

SSH_CONFIG="/etc/ssh/sshd_config"

sudo cp "$SSH_CONFIG" "${SSH_CONFIG}.bak"

sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' "$SSH_CONFIG"
sudo sed -i 's/^#\?ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' "$SSH_CONFIG"
sudo sed -i 's/^#\?UsePAM.*/UsePAM no/' "$SSH_CONFIG"
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' "$SSH_CONFIG"
sudo sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' "$SSH_CONFIG"

echo "Banner /etc/issue.net" >> $SSH_CONFIG

echo "This is just a maintanence port and not apart of the challenge. Please don't try authenticate :)" >> /etc/issue.net

sudo systemctl restart ssh

# ===== Firewall Configuration =====

echo ">>> Setting up firewall"

sudo apt-get update -y
sudo apt-get install -y ufw

sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 22/tcp comment "Maintanence port"
sudo ufw allow 5000/tcp comment ""
sudo ufw allow proto udp from 0.0.0.0/0 to 0.0.0.0/0 port 67 comment "Allow dhcp"

sudo ufw enable

echo ">>> Firewall enabled"

# ===== Access Point Setup =====

echo ">>> Configuring wireless access point"

nmcli con add type wifi ifname wlan0 con-name $SSID autoconnect yes ssid $SSID
nmcli con modify $SSID 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
nmcli con modify $SSID wifi-sec.key-mgmt wpa-psk
nmcli con modify $SSID wifi-sec.psk "$PASSWORD"
nmcli con up $SSID

echo ">>> Creating service to start hotspot on reboot"

echo "[Unit]
Description=Start hotspot for KawaiiCon challenges and maintanence access
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/nmcli con up $SSID
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/KawaiiCon-start-hotspot.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable KawaiiCon-start-hotspot.service
sudo systemctl start KawaiiCon-start-hotspot

echo ">>> Service created, wait about 2 mins after boot for hotspot to appear\n"

# ===== Miscelaneous =====

echo "FLAG{how_did_you_root_the_pi}" > /root/how_did_we_get_here.txt

echo "==== Setup complete ====="
