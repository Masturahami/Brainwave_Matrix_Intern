import re
import time
import csv
import os
import hashlib
import math
import random
import string
import getpass
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

COMMON_PASSWORD_FILE = "common.txt"
BREACH_PASSWORD_FILE = "bridge.txt"
HISTORY_FILE = "history.csv"

# ASCII Cat Art
def cyberpaw_intro():
    print(Fore.MAGENTA + """
     /\\_/\\   CyberPaw is here!
    ( o.o )  Let's check your password.
     > ^ <   Meowgical Security Activated!
    """)

# Generate SHA-256 hashes of common.txt into bridge.txt
def generate_breach_file():
    if not os.path.exists(COMMON_PASSWORD_FILE):
        print(Fore.RED + f"[!] {COMMON_PASSWORD_FILE} not found.")
        return

    with open(COMMON_PASSWORD_FILE, 'r', encoding='utf-8') as f:
        passwords = f.read().splitlines()

    with open(BREACH_PASSWORD_FILE, 'w', encoding='utf-8') as out:
        for pw in passwords:
            hashed = hashlib.sha256(pw.encode()).hexdigest()
            out.write(hashed + '\n')
    print(Fore.GREEN + "[*] bridge.txt generated from common.txt using SHA-256.")

# Load wordlists
def load_wordlist(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        print(Fore.RED + f"[!] {filename} not found. Skipping...")
        return set()

# Entropy calculation
def calculate_entropy(password):
    charset = 0
    if re.search(r"[a-z]", password): charset += 26
    if re.search(r"[A-Z]", password): charset += 26
    if re.search(r"\d", password): charset += 10
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): charset += 32
    return round(len(password) * math.log2(charset)) if charset else 0

# Suggest stronger password
def suggest_stronger_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

# Log password check
def log_history(password, score, remarks):
    fieldnames = ['timestamp', 'password', 'score', 'remarks']
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'password': '*' * len(password),
            'score': score,
            'remarks': remarks
        })

# Password strength checker logic
def check_password_strength(password, common_passwords, breached_hashes):
    remarks = []
    score = 0

    # SHA-256 hash check
    sha256 = hashlib.sha256(password.encode()).hexdigest()
    if sha256 in breached_hashes:
        remarks.append(Fore.RED + "This password has been found in breaches (SHA-256 match).")
        score -= 3

    if password in common_passwords:
        remarks.append(Fore.RED + "Too common! Avoid popular passwords.")
        score -= 2

    length = len(password)
    if length >= 12:
        score += 2
        remarks.append(Fore.GREEN + "Great length!")
    elif length >= 8:
        score += 1
        remarks.append(Fore.YELLOW + "Good length, but could be stronger.")
    else:
        score -= 1
        remarks.append(Fore.RED + "Password too short!")

    if re.search(r"[A-Z]", password):
        score += 1
        remarks.append(Fore.GREEN + "Contains uppercase letters.")
    else:
        remarks.append(Fore.YELLOW + "Consider adding uppercase letters.")

    if re.search(r"[a-z]", password):
        score += 1

    if re.search(r"\d", password):
        score += 1
        remarks.append(Fore.GREEN + "Contains numbers.")
    else:
        remarks.append(Fore.YELLOW + "Consider adding numbers.")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
        remarks.append(Fore.GREEN + "Contains special characters.")
    else:
        remarks.append(Fore.YELLOW + "Try using special characters for better strength.")

    # Repeated characters check
    if re.search(r"(.)\1{2,}", password):
        remarks.append(Fore.YELLOW + "Avoid repeated characters like 'aaa' or '111'.")

    # Entropy feedback
    entropy = calculate_entropy(password)
    if entropy < 40:
        remarks.append(Fore.RED + f"Low entropy ({entropy} bits): Easy to guess.")
    elif entropy < 60:
        remarks.append(Fore.YELLOW + f"Moderate entropy ({entropy} bits).")
    else:
        remarks.append(Fore.GREEN + f"High entropy ({entropy} bits): Strong password.")

    return max(0, score), remarks

# Main interface
def main():
    cyberpaw_intro()

    if not os.path.exists(BREACH_PASSWORD_FILE):
        generate_breach_file()

    common_passwords = load_wordlist(COMMON_PASSWORD_FILE)
    breached_hashes = load_wordlist(BREACH_PASSWORD_FILE)

    while True:
        print(Style.BRIGHT + "\nEnter a password to check or type 'exit' to quit.")
        password = getpass.getpass(Fore.CYAN + ">>> ")

        if password.lower() == 'exit':
            print(Fore.MAGENTA + "CyberPaw is curling up for a nap. Bye!")
            break

        score, remarks = check_password_strength(password, common_passwords, breached_hashes)

        print(Fore.CYAN + "\n[CyberPaw's Report]")
        for remark in remarks:
            print(" -", remark)

        print(Fore.MAGENTA + f"\nFinal Score: {score}/8")

        if score >= 7:
            print(Fore.GREEN + "CyberPaw purrs: That password is pawsitively strong!")
        elif score >= 4:
            print(Fore.YELLOW + "CyberPaw meows: It's decent, but could be better.")
        else:
            print(Fore.RED + "CyberPaw hisses: That password is too weak!")
            print(Fore.BLUE + f"Try something like: {suggest_stronger_password()}")

        log_history(password, score, ' | '.join([r.strip(Style.RESET_ALL) for r in remarks]))

        time.sleep(1)

if __name__ == "__main__":
    main()
