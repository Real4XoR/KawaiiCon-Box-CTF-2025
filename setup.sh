#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
    echo "run as root" >&2
    exit 1
fi

# === CONFIGURATION ===

USER="raspberry" 
HOME_DIR="/home/$USER"
SSH_DIR="$HOME_DIR/.ssh"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"

SSID="BlackBoxZero"
PASSWORD="whosetthisshittypassword"

PUBLIC_KEYS=(
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDpj9EFTdCIGm60Im6ZltQZ53kEIJ7YiUwfpBVmnFCjJ ncobbald@Laptops-MacBook-Pro.local"
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE5HKN7vqMDm2aEAN63mgjhN/bGha9kdHEqDqEawz+YI bskerman@C02C204LJHD3s-MacBook-Pro.local"
)


echo "=== BlackBoxZero Setup Starting ==="

# === SSH CONFIGURATION ===

echo ">>> Configuring SSH access and keys..."

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

# === FIREWALL CONFIGURATION ===

echo ">>> Setting up firewall (UFW)..."

sudo apt-get update -y
sudo apt-get install -y ufw

sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 22/tcp
sudo ufw allow 5000/tcp
sudo ufw allow proto udp from 0.0.0.0/0 to 0.0.0.0/0 port 67 comment "Allow dhcp"

sudo ufw enable
echo ">>> UFW enabled: SSH allowed from any IP"

# === ACCESS POINT SETUP VIA NETWORKMANAGER ===

echo ">>> Configuring Wi-Fi Access Point via NetworkManager..."

sudo apt-get install -y network-manager

sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

sudo nmcli connection delete "$SSID" >/dev/null 2>&1 || true

sudo nmcli device set wlan0 managed yes

sudo nmcli connection add type wifi ifname wlan0 mode ap con-name "$SSID" ssid "$SSID"
sudo nmcli connection modify "$SSID" \
    802-11-wireless.band bg \
    802-11-wireless.channel 7 \
    ipv4.addresses 192.168.4.1/24 \
    ipv4.method shared \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "$PASSWORD"

sudo nmcli connection up "$SSID"

echo ">>> Access Point '$SSID' is active."
echo "    SSID: $SSID"
echo "    Password: $PASSWORD"
echo "    Pi IP address on AP network: 192.168.4.1"

echo "=== BlackBoxZero setup complete ==="
