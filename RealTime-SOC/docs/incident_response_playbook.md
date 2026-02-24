# 📖 Incident Response Playbook
## RealTime-SOC — Wazuh-Based SOC

---

## Overview

This playbook defines the detection, analysis, containment, eradication, and recovery (DACER) steps for the top attack scenarios monitored by this SOC.

---

## Playbook 1: SSH Brute-Force Attack

### 🔴 Trigger
- Wazuh Rule IDs: **100200** (10 failures/60s) or **100201** (5 failures/120s)
- Alert Level: 10–12

### 🔍 Detection
1. Open Wazuh Dashboard → **Threat Hunting** → search `rule.id:100200`
2. Note source IP, targeted agent, and timestamps
3. Correlate with `auth.log`: `docker exec wazuh.agent grep <srcip> /var/log/auth.log`

### 🔒 Containment (Automated)
- Active response script `custom-block-ip.sh` automatically runs and blocks the source IP via `iptables DROP`
- A Telegram/Discord notification is sent with the details

### Manual Verification
```bash
# Confirm block is in place
docker exec wazuh.agent iptables -L INPUT | grep <srcip>

# View block log
docker exec wazuh.manager cat /var/ossec/logs/blocked_ips.log
```

### 🧹 Eradication
1. Investigate whether any login succeeded: `grep "Accepted" /var/log/auth.log`
2. If login succeeded — escalate to **Playbook: Account Compromise**
3. Force-expire the affected account: `passwd -l <username>`

### 📈 Recovery
1. Harden SSH config: `PasswordAuthentication no`, `MaxAuthTries 3`
2. Implement SSH key-only authentication
3. Unblock IP after 10 mins (auto-timeout) or manually: `iptables -D INPUT -s <IP> -j DROP`

---

## Playbook 2: Reverse Shell Attempt

### 🔴 Trigger
- Wazuh Rule IDs: **100300**, **100301**, **100302**
- Alert Level: 15 (Critical)

### 🔍 Detection
1. Dashboard → **Security Events** → filter `rule.id:(100300 OR 100301 OR 100302)`
2. Identify executing user and parent process from `full_log` field
3. Check process tree: `docker exec wazuh.agent ps auxf | grep <pid>`

### 🔒 Containment
1. Immediately isolate the agent from the network if confirmed:
   ```bash
   docker exec wazuh.agent iptables -I OUTPUT -j DROP
   ```
2. Capture memory artifacts before killing process:
   ```bash
   docker exec wazuh.agent cat /proc/<pid>/maps > /tmp/mem_map_<ts>.txt
   ```
3. Kill the suspicious process: `kill -9 <pid>`

### 🧹 Eradication
1. Scan for dropped files in `/tmp`, `/dev/shm`: `find /tmp /dev/shm -newer /etc/passwd -ls`
2. Remove any malicious files found
3. Check crontabs for persistence: `crontab -l && cat /etc/crontab`
4. Reset any modified credentials

### 📈 Recovery
1. Rebuild the container from a clean image if compromise confirmed
2. Patch the entry-point vulnerability (web app, misconfigured service)

---

## Playbook 3: Suspicious File Modification (FIM Alert)

### 🔴 Trigger
- Wazuh Rule IDs: **100400** (`/etc/passwd`, `/etc/shadow`), **100402** (crontab)
- Alert Level: 10–11

### 🔍 Detection
1. Dashboard → **Integrity Monitoring** → view changed attributes
2. Compare hash from alert vs. known good: `sha256sum /etc/passwd`
3. Check who modified the file: `ausearch -f /etc/passwd`

### 🔒 Containment
1. If unauthorized modification: restore from backup
   ```bash
   cp /backup/etc/passwd /etc/passwd
   ```
2. Lock the account if shadow was modified: `passwd -l <user>`

### 🧹 Eradication
1. Review recent `sudo` and `su` events in `auth.log`
2. Audit user accounts: `awk -F: '$3 == 0 {print $1}' /etc/passwd` (look for extra root accounts)

### 📈 Recovery
1. Restore file from backup and verify hash
2. Enable `auditd` rules on critical files

---

## Playbook 4: Docker Privilege Escalation

### 🔴 Trigger
- Wazuh Rule IDs: **100500**, **100501**, **100502**
- Alert Level: 13–14

### 🔍 Detection
1. Dashboard → filter `rule.id:(100500 OR 100501 OR 100502)`
2. Identify container name and image from Wazuh's Docker listener logs
3. Inspect container: `docker inspect <container_id>`

### 🔒 Containment
```bash
# Immediately stop the suspicious container
docker stop <container_id>

# Remove it
docker rm <container_id>
```

### 🧹 Eradication
1. Audit all running containers for `--privileged` flag:
   ```bash
   docker ps -q | xargs docker inspect --format '{{.Name}} {{.HostConfig.Privileged}}'
   ```
2. Audit for Docker socket mounts:
   ```bash
   docker ps -q | xargs docker inspect --format '{{.Name}} {{.Mounts}}' | grep docker.sock
   ```
3. Remove any unauthorized images: `docker image prune -a`

### 📈 Recovery
1. Enforce Docker security policy: no `--privileged` in production
2. Use rootless Docker (`dockerd` in user namespace)
3. Implement AppArmor/Seccomp profiles

---

## Playbook 5: Port Scan Detection

### 🔴 Trigger
- Wazuh Rule IDs: **100600**, **100601** (from Suricata EVE)
- Alert Level: 7–9

### 🔍 Detection
1. Dashboard → **Threat Intelligence** → filter `rule.id:100600`
2. Identify scanning IP, scan type (SYN, UDP, etc.)
3. Check Suricata fast.log: `docker exec suricata tail -100 /var/log/suricata/fast.log`

### 🔒 Containment
1. Block the scanning IP at the firewall:
   ```bash
   iptables -I INPUT -s <scanning_ip> -j DROP
   ```
2. Alert incident response team

### 📈 Recovery
1. Review and minimize exposed ports in `docker-compose.yml`
2. Implement rate limiting on open services
3. Add the IP to threat intel blocklist

---

## RACI Matrix

| Activity             | SOC Analyst | SOC Lead | CISO | Legal |
|---------------------|-------------|----------|------|-------|
| Initial Detection    | R, A        | I        | I    |       |
| Containment          | R           | A        | I    |       |
| Eradication          | R           | A        | I    |       |
| Recovery             | R           | A        | I    |       |
| Post-Mortem          | C           | R, A     | I    |       |
| Legal Escalation     | I           | R        | A    | R, A  |

---

## Severity Classification

| Level | Wazuh Levels | Description                         | Response SLA |
|-------|-------------|-------------------------------------|--------------|
| P1    | 15+         | Critical — active breach            | Immediate    |
| P2    | 12–14       | High — active attack confirmed      | 15 minutes   |
| P3    | 9–11        | Medium — attack pattern detected    | 1 hour       |
| P4    | 7–8         | Low — suspicious activity           | 4 hours      |
| P5    | <7          | Info — logged only                  | Best effort  |
