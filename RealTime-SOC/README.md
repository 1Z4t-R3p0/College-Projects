# Real-Time SOC Monitoring & Incident Response System

> A production-grade Security Operations Center stack built with **Wazuh 4.7.2**, **OpenSearch**, and a custom **Python SOC Monitor UI**. Designed for real-time threat detection, automated brute-force detection, and visual incident response.

---

## ⚡ One-Click Deployment


### 🐧 WSL / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/1Z4t-R3p0/College-Projects/main/RealTime-SOC/linux-setup.sh | bash
```

### 🛠️ Manual Local Setup (Clone & Run)

```bash
git clone https://github.com/1Z4t-R3p0/College-Projects.git
cd College-Projects/RealTime-SOC
chmod +x setup.sh
./setup.sh
```

---

## 🖥️ Dashboard Access

Once deployed, access the system through two interfaces:

| Interface | URL | Purpose |
| :--- | :--- | :--- |
| **Quick SOC Monitor** | [http://localhost:8080](http://localhost:8080) | Real-time attack feed with incident type stamps |
| **Wazuh Dashboard** | [http://localhost:443](http://localhost:443) | Full SIEM — threat hunting, compliance, FIM |

**Credentials** → Username: `admin` | Password: *(Security plugin disabled for demo)*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network (soc_net)              │
│                                                         │
│  ┌───────────────┐      ┌───────────────────────────┐   │
│  │  Wazuh Agent  │─────▶│     Wazuh Manager 4.7.2   │   │
│  │  (Endpoint)   │      │  (Analysis + Rule Engine)  │   │
│  └───────────────┘      └─────────────┬─────────────┘   │
│                                       │ Filebeat         │
│                         ┌─────────────▼─────────────┐   │
│                         │   Wazuh Indexer (OpenSearch│   │
│                         │        2.11.0)             │   │
│                         └─────────────┬─────────────┘   │
│                                       │                  │
│            ┌──────────────────────────┤                  │
│            │                          │                  │
│  ┌─────────▼──────┐      ┌────────────▼─────────────┐   │
│  │   SOC Monitor   │      │  OpenSearch Dashboard     │   │
│  │   (Port 8080)   │      │     (Port 443)            │   │
│  └────────────────┘      └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛡️ Security Features

| Feature | Description |
| :--- | :--- |
| **SSH Brute Force Detection** | Triggers at 8+ failed login attempts; escalates to Level 10 alert |
| **Privilege Escalation Monitoring** | Real-time alerts on `sudo` abuse and unauthorized root execution |
| **File Integrity Monitoring (FIM)** | Tracks changes to `/etc`, `/bin`, `/root` |
| **Docker Runtime Monitoring** | Detects container anomalies via Docker socket listener |
| **Custom SOC Monitor UI** | Python/Flask dashboard showing live attack stamps (Brute Force, Priv. Esc.) |
| **Policy Compliance (SCA)** | Automated CIS Benchmark checks |

---

## 🎯 Attack Simulation

To verify the system is detecting threats, run the interactive simulation suite:

```bash
./scripts/simulate_attacks.sh
```

Press **Enter** at each prompt to run through the scenarios:

1. **Scenario 1 — SSH Brute Force**: Simulates 10+ failed SSH logins; triggers Level 10 alert on the SOC Monitor.
2. **Scenario 2 — Privilege Escalation**: Injects `sudo` abuse patterns; classified as "Privilege Escalation" in the UI.

> Watch the **Quick SOC Monitor** ([http://localhost:8080](http://localhost:8080)) update in real time with colour-coded incident type stamps.

---

## 📦 Project Structure

```
RealTime-SOC/
│
├── setup.sh                    # One-command deployment script
├── docker-compose.yml          # Full stack definition (5 services)
│
├── config/
│   ├── wazuh_manager/
│   │   └── ossec.conf          # Manager rules, log sources, FIM settings
│   └── wazuh_agent/
│       ├── Dockerfile          # Agent image
│       ├── ossec.conf          # Agent configuration
│       └── agent-entrypoint.sh # Registration & startup script
│
├── soc-monitor/
│   ├── app.py                  # Flask backend + attack classification engine
│   ├── Dockerfile
│   └── templates/
│       └── index.html          # Real-time SOC Monitor frontend
│
└── scripts/
    └── simulate_attacks.sh     # Interactive attack simulation suite
```

---

## ⚙️ System Requirements

| Resource | Minimum | Recommended |
| :--- | :--- | :--- |
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 20 GB free | 40 GB free |
| **Docker** | 24.x+ | Latest |
| **Docker Compose** | v2.x+ | Latest |

> `setup.sh` will **automatically install** Docker and Docker Compose if they are not present.

---

## 📖 Academic Reference

This project demonstrates key Computer Science & Cyber Security concepts:

- **SIEM** — Security Information & Event Management (Wazuh)
- **Containerisation** — Docker-based multi-service orchestration
- **Incident Response** — Automated classification and alerting
- **DevSecOps** — Infrastructure-as-code security deployment

---

**Maintained by** [1Z4t-R3p0](https://github.com/1Z4t-R3p0) · **License**: MIT
