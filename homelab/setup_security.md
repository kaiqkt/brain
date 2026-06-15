---
title: "Home Lab — Setup & Security"
tags: [homelab, ubuntu, self-hosted, security, oss]
domain: dev
type: reference
sources: []
created: 2026-06-15
updated: 2026-06-15
---

# Home Lab — Setup & Security

Ubuntu Server headless. Goal: run local and self-hosted projects for personal use. Focus on security, minimalism and OSS.

> **Note:** all commands below assume you are logged in as `kaiqkt`. Use `sudo` on each command that requires root — do not chain with `&&` without sudo on each part.

## 1. User & SSH

Creates a dedicated user, disables remote root and restricts access to public key. No password = no brute force.

```bash
sudo adduser kaiqkt
sudo usermod -aG sudo kaiqkt

# On client (Mac/Linux)
ssh-copy-id -i ~/.ssh/id_ed25519.pub kaiqkt@<server-ip>
```

`/etc/ssh/sshd_config` — edit with `sudo vim /etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowUsers kaiqkt
```

```bash
sudo systemctl reload ssh
```

> Port 22 kept — local server, key-only auth + Fail2ban is sufficient protection. Changing port is security through obscurity with no real gain here.

**Verify:**
```bash
grep -v '^#' /etc/ssh/sshd_config | grep -v '^$'
cat ~/.ssh/authorized_keys
```

---

## 2. Firewall — UFW

Blocks all incoming traffic by default. Opens ports explicitly as each service comes up. Principle of least privilege on the network.

```bash
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw enable
sudo ufw status verbose
```

> Additional rules as each service starts. E.g.: `sudo ufw allow 80/tcp` only when Traefik is active.

**Verify:**
```bash
sudo ufw status verbose
```

---

## 3. Fail2ban

Monitors logs and bans IPs that exceed login attempts. Complements key-only auth by blocking scanners and bots before they accumulate noise.

```bash
sudo apt install fail2ban -y
```

Create `/etc/fail2ban/jail.local` with `sudo vim /etc/fail2ban/jail.local`:
```ini
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled  = true
port     = 22
logpath  = %(sshd_log)s
backend  = %(sshd_backend)s
```

```bash
sudo systemctl enable --now fail2ban
```

**Verify:**
```bash
sudo fail2ban-client status sshd
```

---

## 4. Auto-Updates

Applies security patches automatically without manual intervention. Reboots remain manual to avoid taking down services at the wrong time.

```bash
sudo apt install unattended-upgrades apt-listchanges -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Edit `/etc/apt/apt.conf.d/50unattended-upgrades` with `sudo vim` (file already exists — do not create):
```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}:${distro_codename}-updates";
};
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Mail "kaiquebeserra1313@gmail.com";
```

**Verify:**
```bash
sudo unattended-upgrades --dry-run --debug 2>&1 | head -20
```

---

## 5. Minimize Surface

Disables services that will not be used. Each running process is unnecessary attack surface.

```bash
sudo systemctl disable --now snapd avahi-daemon cups bluetooth 2>/dev/null

# Audit what's running
systemctl list-units --type=service --state=running

# Clean packages
sudo apt autoremove --purge -y && sudo apt clean
```

---

## 6. AppArmor

Confines processes to access profiles (files, network, syscalls). Limits damage if a service is compromised. Already active on Ubuntu.

```bash
sudo apt install apparmor-utils -y
sudo aa-status
```

---

## 7. Audit — Logwatch

Daily system activity report. Runs via cron — not a systemd service.

```bash
sudo apt install logwatch -y
```

**Verify installation:**
```bash
ls /etc/cron.daily/ | grep logwatch   # should list 00logwatch
sudo logwatch --output stdout --detail low --range today
```

---

## 8. Docker

Container runtime to isolate services. Each project runs in its own container without interfering with the base system.

```bash
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings

# GPG key — sudo on both curl and gpg
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Repo — single line command, use tee with sudo
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update && sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
sudo usermod -aG docker kaiqkt
```

> After `usermod`, logout and login for the `docker` group to be recognized.

`/etc/docker/daemon.json` — create with `sudo vim /etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "no-new-privileges": true,
  "userland-proxy": false
}
```

```bash
sudo systemctl restart docker
```

**Verify:**
```bash
docker version
docker run --rm hello-world
```

---

## 9. Remote Access — Tailscale

OSS mesh VPN. Zero ports open on the internet. Access the server from anywhere via Tailscale IP without exposing ports on the router.

**On the server (nerv):**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**On Mac (CLI via Homebrew — no GUI app):**
```bash
brew install tailscale

# Start as system service (needs root — tailscaled requires root to create tun interface)
sudo brew services start tailscale

tailscale up   # opens link in terminal — authenticate in browser with the same account
```

> `brew services start tailscale` (without sudo) fails with `tailscaled requires root`. Always use `sudo brew services start tailscale`.

**Verify:**
```bash
tailscale status          # lists all devices on the network
tailscale ping nerv       # tests latency and connection mode (direct vs DERP relay)
brew services list | grep tailscale   # should show "started" and root as owner
```

**Connect to nerv:**
```bash
ssh kaiqkt@100.95.195.104
```

> IP `100.95.195.104` is fixed as long as the account exists. Works from any network.

### Troubleshooting — Mac

**tailscaled logs appearing in terminal:**
`tailscaled` was started manually in foreground instead of as a service. Fix:
```bash
sudo pkill tailscaled
sudo brew services start tailscale
```

**`tailscale status` returns "failed to connect to local Tailscale service":**
Service is not running or failed to start.
```bash
brew services list | grep tailscale          # check status
cat /opt/homebrew/var/log/tailscaled.log     # read the actual error
sudo brew services restart tailscale         # restart
```

**LinkChange / DERP "connection reset by peer" in logs:**
Normal — happens after network change (DHCP renewal, WiFi switch). Tailscale reconnects automatically. No action required.

---

## Execution Order

1. User & SSH hardening
2. UFW
3. Fail2ban
4. Unattended-upgrades
5. Minimize Surface
6. AppArmor
7. Logwatch
8. Docker
9. Tailscale
10. Traefik (when first web project goes up)
