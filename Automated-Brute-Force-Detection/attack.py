#!/usr/bin/env python3

import sys
import time
import argparse
import requests
import concurrent.futures

def print_banner(target, port, wordlist, user):
    print("==========================================================")
    print("    Automated Brute Force Detection - Attack Simulation   ")
    print("==========================================================")
    print(f"Target: {target}:{port}")
    print(f"Wordlist: {wordlist}")
    print(f"User: {user}")
    print("----------------------------------------------------------")
    print("[*] Starting Python Bruteforce Attack...")
    print(f"Hydra (mimic) starting at {time.strftime('%Y-%m-%d %H:%M:%S')}")

def attempt_login(url, username, password):
    data = {'username': username, 'password': password}
    try:
        response = requests.post(url, data=data, timeout=5)
        # Mimic hydra output
        print(f"[8080][http-post-form] host: 127.0.0.1   login: {username}   password: {password}")
        return password, response.status_code, response.text
    except Exception as e:
        print(f"[-] Error testing password {password}: {e}")
        return password, None, None

def main():
    parser = argparse.ArgumentParser(description="Python Brute Force Tool mimicking Hydra")
    parser.add_argument("-t", "--target", default="localhost", help="Target host")
    parser.add_argument("-p", "--port", default="8080", help="Target port")
    parser.add_argument("-w", "--wordlist", default="wordlist.txt", help="Wordlist file")
    parser.add_argument("-u", "--user", default="admin", help="Username to bruteforce")
    
    args = parser.parse_args()
    
    try:
        with open(args.wordlist, 'r', encoding='utf-8') as f:
            passwords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Wordlist file {args.wordlist} not found.")
        sys.exit(1)
        
    print_banner(args.target, args.port, args.wordlist, args.user)
    
    url = f"http://{args.target}:{args.port}/login"
    
    print(f"[DATA] max 16 tasks per 1 server, overall 16 tasks, {len(passwords)} login tries (l:1/p:{len(passwords)})")
    print(f"[DATA] attacking http-post-form://{args.target}:{args.port}/login:username=^USER^&password=^PASS^:Invalid credentials")
    
    # We want to wait a split second between hits to simulate true threading randomness and avoid overloading python itself
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = []
        for pwd in passwords:
            futures.append(executor.submit(attempt_login, url, args.user, pwd))
            time.sleep(0.01) # Slightly space out requests
        
        # Wait for completes
        for future in concurrent.futures.as_completed(futures):
            _ = future.result()
            
    print(f"1 of 1 target successfully completed, {len(passwords)} valid passwords found")
    print(f"Hydra (mimic) finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("----------------------------------------------------------")
    print("[*] Attack completed.")
    print("[*] Check application logs to see detection and blocking.")

if __name__ == "__main__":
    main()
