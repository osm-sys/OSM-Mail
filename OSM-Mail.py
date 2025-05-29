#!/usr/bin/env python3
import os
import sys
import time
import random
from datetime import datetime, timedelta

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

# OSM logo
OSM_LOGO = fr"""{RED}
   ___    __  __
  / _ \  |  \/  |
 | |O| | | \  / |
 | |S| | | |\/| |
 | |M| | | |  | |
  \___/  |_|  |_|
{RESET}"""

class FakeEmailSystem:
    def __init__(self):
        self.domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "osm.org"]
        self.inbox = []
        self.service_templates = {
            "google": {
                "subject": "Your Google verification code",
                "body": "G-{code} is your Google verification code.\n\nDon't share this code with anyone.",
                "expiry": 5  # minutes
            },
            "instagram": {
                "subject": "Your Instagram confirmation code",
                "body": f"Your Instagram confirmation code is: {BOLD}{{code}}{RESET}\n\nEnter this code to confirm your account.",
                "expiry": 10
            },
            "facebook": {
                "subject": "Facebook login code",
                "body": "Your Facebook login code is: {code}\n\nThis code will expire in 15 minutes.",
                "expiry": 15
            },
            "twitter": {
                "subject": "Your Twitter confirmation code",
                "body": "Your Twitter confirmation code is: {code}\n\nThis code expires in {expiry} minutes.",
                "expiry": 30
            },
            "amazon": {
                "subject": "Your Amazon OTP",
                "body": "Your Amazon one-time password (OTP) is: {code}\n\nValid for {expiry} minutes only.",
                "expiry": 10
            }
        }

    def generate_email(self, username=None):
        if username is None:
            username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=8))
        domain = random.choice(self.domains)
        return f"{username}@{domain}"

    def generate_verification_code(self, service):
        if service.lower() not in self.service_templates:
            return None
        
        template = self.service_templates[service.lower()]
        code_length = 6 if service.lower() == "google" else 8
        code = ''.join([str(random.randint(0, 9)) for _ in range(code_length)])
        
        if service.lower() == "google":
            code = f"G-{code}"
        
        expiry_time = datetime.now() + timedelta(minutes=template['expiry'])
        
        email = {
            "from": f"noreply@{service.lower()}.com",
            "subject": template['subject'],
            "body": template['body'].format(code=code, expiry=template['expiry']),
            "received": datetime.now(),
            "service": service,
            "code": code,
            "expires": expiry_time,
            "read": False
        }
        
        self.inbox.append(email)
        return email

    def check_inbox(self):
        return sorted(self.inbox, key=lambda x: x['received'], reverse=True)

    def mark_as_read(self, index):
        if 0 <= index < len(self.inbox):
            self.inbox[index]['read'] = True
            return True
        return False

def print_menu():
    print("\n" + "="*50)
    print(f"{BOLD}OSM Fake Email & Verification System{RESET}")
    print("="*50)
    print(f"{BOLD}1.{RESET} Generate new fake email")
    print(f"{BOLD}2.{RESET} Generate verification code (Google/Instagram/etc)")
    print(f"{BOLD}3.{RESET} View inbox")
    print(f"{BOLD}4.{RESET} Clear inbox")
    print(f"{BOLD}5.{RESET} Exit")
    print("="*50)

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(OSM_LOGO)
    
    email_system = FakeEmailSystem()
    current_email = None

    while True:
        print_menu()
        choice = input(f"\n{BOLD}Select an option: {RESET}")

        if choice == "1":
            current_email = email_system.generate_email()
            print(f"\n{GREEN}Generated email:{RESET} {BOLD}{current_email}{RESET}")
            input(f"\n{BLUE}Press Enter to continue...{RESET}")

        elif choice == "2":
            if not current_email:
                print(f"\n{RED}Please generate an email first!{RESET}")
                time.sleep(1)
                continue

            print("\nAvailable services:")
            for i, service in enumerate(email_system.service_templates.keys(), 1):
                print(f"{BOLD}{i}.{RESET} {service.capitalize()}")
            
            service_choice = input(f"\n{BOLD}Select service: {RESET}")
            try:
                service_index = int(service_choice) - 1
                service = list(email_system.service_templates.keys())[service_index]
                email = email_system.generate_verification_code(service)
                print(f"\n{GREEN}Verification code generated!{RESET}")
                print(f"\n{BOLD}From:{RESET} {email['from']}")
                print(f"{BOLD}Subject:{RESET} {email['subject']}")
                print(f"\n{email['body']}")
                print(f"\n{BLUE}This code expires at: {email['expires'].strftime('%H:%M:%S')}{RESET}")
                input(f"\n{BLUE}Press Enter to continue...{RESET}")
            except (ValueError, IndexError):
                print(f"\n{RED}Invalid service selection!{RESET}")
                time.sleep(1)

        elif choice == "3":
            if not current_email:
                print(f"\n{RED}Please generate an email first!{RESET}")
                time.sleep(1)
                continue

            inbox = email_system.check_inbox()
            if not inbox:
                print(f"\n{YELLOW}Inbox is empty{RESET}")
                input(f"\n{BLUE}Press Enter to continue...{RESET}")
                continue

            print(f"\n{BOLD}Inbox for: {current_email}{RESET}")
            print("-"*50)
            for i, email in enumerate(inbox, 1):
                status = f"{RED}UNREAD{RESET}" if not email['read'] else f"{GREEN}read{RESET}"
                print(f"{BOLD}{i}.{RESET} [{status}] {email['from']} - {email['subject']}")
                print(f"   Received: {email['received'].strftime('%Y-%m-%d %H:%M:%S')}")
                print("-"*50)

            view_choice = input(f"\n{BOLD}Enter number to view (0 to go back): {RESET}")
            if view_choice == "0":
                continue
            try:
                email_index = int(view_choice) - 1
                if 0 <= email_index < len(inbox):
                    email = inbox[email_index]
                    email_system.mark_as_read(email_index)
                    print(f"\n{BOLD}From:{RESET} {email['from']}")
                    print(f"{BOLD}Subject:{RESET} {email['subject']}")
                    print(f"{BOLD}Received:{RESET} {email['received'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"{BOLD}Expires:{RESET} {email['expires'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print("\n" + email['body'])
                    input(f"\n{BLUE}Press Enter to continue...{RESET}")
                else:
                    print(f"\n{RED}Invalid message number!{RESET}")
                    time.sleep(1)
            except ValueError:
                print(f"\n{RED}Invalid input!{RESET}")
                time.sleep(1)

        elif choice == "4":
            email_system.inbox = []
            print(f"\n{GREEN}Inbox cleared!{RESET}")
            time.sleep(1)

        elif choice == "5":
            print(f"\n{GREEN}Exiting OSM Fake Email System. Goodbye!{RESET}")
            sys.exit(0)

        else:
            print(f"\n{RED}Invalid choice!{RESET}")
            time.sleep(1)

        os.system('clear' if os.name == 'posix' else 'cls')
        print(OSM_LOGO)

if __name__ == "__main__":
    main()
