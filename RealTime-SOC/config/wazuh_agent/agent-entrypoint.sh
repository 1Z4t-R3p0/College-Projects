#!/bin/bash
set -e

MANAGER="${WAZUH_MANAGER:-wazuh.manager}"
GROUP="${WAZUH_AGENT_GROUP:-default}"
REG_PASS="${WAZUH_REGISTRATION_PASSWORD:-SecretPassword}"

echo "[*] Configuring Wazuh agent to connect to manager: $MANAGER"

# Write ossec.conf
cat > /var/ossec/etc/ossec.conf <<EOF
<ossec_config>
  <client>
    <server>
      <address>${MANAGER}</address>
      <port>1514</port>
      <protocol>tcp</protocol>
    </server>
    <config-profile>ubuntu, ubuntu22</config-profile>
    <notify_time>10</notify_time>
    <time-reconnect>60</time-reconnect>
    <auto_restart>yes</auto_restart>
  </client>

  <logging>
    <log_format>plain</log_format>
  </logging>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/syslog</location>
  </localfile>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/auth.log</location>
  </localfile>

  <localfile>
    <log_format>json</log_format>
    <location>/var/log/suricata/eve.json</location>
  </localfile>

  <wodle name="docker-listener">
    <disabled>no</disabled>
    <interval>10m</interval>
    <run_on_start>yes</run_on_start>
  </wodle>

  <syscheck>
    <disabled>no</disabled>
    <frequency>300</frequency>
    <scan_on_start>yes</scan_on_start>
    <directories check_all="yes" realtime="yes">/etc,/usr/bin,/usr/sbin</directories>
    <directories check_all="yes" realtime="yes">/bin,/sbin</directories>
    <directories check_all="yes" report_changes="yes" realtime="yes">/root</directories>
  </syscheck>

  <rootcheck>
    <disabled>no</disabled>
    <frequency>43200</frequency>
  </rootcheck>

  <active-response>
    <disabled>no</disabled>
  </active-response>
</ossec_config>
EOF

echo "[*] Registering agent with manager..."
/var/ossec/bin/agent-auth \
    -m "${MANAGER}" \
    -G "${GROUP}" || true

echo "[*] Starting Wazuh agent..."
exec /var/ossec/bin/wazuh-agentd -f
