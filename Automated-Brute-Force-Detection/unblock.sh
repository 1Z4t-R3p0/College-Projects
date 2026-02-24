#!/bin/bash

# Default to "all" if no IP is specified
IP=${1:-"all"}

echo "=========================================="
echo "    Brute Force Unblock Utility"
echo "=========================================="

if [ "$IP" == "all" ]; then
    echo "[*] Unblocking ALL IP addresses..."
    docker compose exec redis redis-cli FLUSHALL
    echo "[+] Done. All restrictions have been cleared."
else
    echo "[*] Unblocking specific IP: $IP..."
    docker compose exec redis redis-cli DEL "blocked:$IP"
    docker compose exec redis redis-cli DEL "failed:$IP"
    echo "[+] Done. Restrictions for $IP have been cleared."
fi
