#!/bin/bash
# =============================================================================
# Wazuh Active Response: Custom IP Blocker
# File: /var/ossec/active-response/bin/custom-block-ip.sh
# Description: Blocks/unblocks attacker IPs using iptables when triggered
#              by Wazuh rules (brute-force, reverse shell, etc.)
# =============================================================================

LOCAL=$(dirname "$0")
cd "$LOCAL"
cd "../"

PWD=$(pwd)
echo "$(date) $0 $1 $2 $3 $4 $5" >> "${PWD}/logs/active-response.log"

# ----------------------------------------
# Parse arguments from Wazuh
# $1 = add or delete
# $2 = user
# $3 = IP address
# $4 = alert_id
# $5 = rule_id
# ----------------------------------------

ACTION=$1
USER=$2
IP=$3
ALERT_ID=$4
RULE_ID=$5

LOG_FILE="${PWD}/logs/active-response.log"
BLOCKED_LOG="/var/ossec/logs/blocked_ips.log"

if [ -z "$IP" ] || [ "$IP" == "-" ]; then
    echo "$(date) [ERROR] No IP address provided. Exiting." >> "$LOG_FILE"
    exit 1
fi

# Validate IP format (basic regex)
if ! echo "$IP" | grep -qE '^([0-9]{1,3}\.){3}[0-9]{1,3}$'; then
    echo "$(date) [ERROR] Invalid IP format: $IP. Exiting." >> "$LOG_FILE"
    exit 1
fi

# Protect localhost / RFC1918 ranges from being accidentally blocked
if echo "$IP" | grep -qE '^(127\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)'; then
    echo "$(date) [WARN] Skipping block of private/loopback IP: $IP" >> "$LOG_FILE"
    exit 0
fi

case "$ACTION" in
    add)
        echo "$(date) [BLOCK] Blocking IP: $IP (Rule: $RULE_ID, Alert: $ALERT_ID)" >> "$LOG_FILE"

        # Block inbound traffic from attacker IP
        iptables -I INPUT -s "$IP" -j DROP
        iptables -I FORWARD -s "$IP" -j DROP

        # Log to blocked IPs file
        echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"action\": \"blocked\", \"ip\": \"$IP\", \"rule_id\": \"$RULE_ID\", \"alert_id\": \"$ALERT_ID\"}" >> "$BLOCKED_LOG"

        echo "$(date) [BLOCK] iptables DROP rule installed for $IP" >> "$LOG_FILE"
        ;;

    delete)
        echo "$(date) [UNBLOCK] Removing block for IP: $IP (Rule: $RULE_ID)" >> "$LOG_FILE"

        # Remove the block
        iptables -D INPUT -s "$IP" -j DROP 2>/dev/null
        iptables -D FORWARD -s "$IP" -j DROP 2>/dev/null

        # Log unblock
        echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"action\": \"unblocked\", \"ip\": \"$IP\", \"rule_id\": \"$RULE_ID\"}" >> "$BLOCKED_LOG"

        echo "$(date) [UNBLOCK] iptables rules removed for $IP" >> "$LOG_FILE"
        ;;

    *)
        echo "$(date) [ERROR] Unknown action: $ACTION" >> "$LOG_FILE"
        exit 1
        ;;
esac

exit 0
