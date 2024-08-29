from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
import json
import os
import random
import string
import getpass
from cryptography.fernet import Fernet
import threading
import time
import sys
import subprocess

# Initialize the rich console
console = Console()

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
KEY_FILE = os.path.join(SCRIPT_DIR, 'key.key')
PROGRAM_PASSWORD_FILE = os.path.join(SCRIPT_DIR, 'program_password.txt')
INFO_FILE = os.path.join(SCRIPT_DIR, 'info.json')

# Function to clear the console
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to generate a secure password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation.replace('\'"\\', '')
    return ''.join(random.choice(characters) for _ in range(length))

# Function to encrypt text
def encrypt_text(text, key):
    fernet = Fernet(key)
    return fernet.encrypt(text.encode()).decode()

# Function to decrypt text
def decrypt_text(encrypted_text, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text.encode()).decode()

# Function to generate or load encryption key
def get_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as file:
            file.write(key)
        return key

# Function to save credentials to a JSON file
def save_credentials(credentials, key):
    encrypted_credentials = [
        {
            'email/uname': encrypt_text(cred['email/uname'], key),
            'website': encrypt_text(cred['website'], key),
            'password': encrypt_text(cred['password'], key)
        } for cred in credentials
    ]
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(encrypted_credentials, file, indent=4)

# Function to load credentials from a JSON file
def load_credentials(key):
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            encrypted_credentials = json.load(file)
        return [
            {
                'email/uname': decrypt_text(cred['email/uname'], key),
                'website': decrypt_text(cred['website'], key),
                'password': decrypt_text(cred['password'], key)
            } for cred in encrypted_credentials
        ]
    return []

# Function to set the program password
def set_program_password():
    password = getpass.getpass("Set a new program password: ")
    with open(PROGRAM_PASSWORD_FILE, 'w') as file:
        file.write(encrypt_text(password, get_key()))

# Function to verify the program password
def verify_program_password():
    if not os.path.exists(PROGRAM_PASSWORD_FILE):
        set_program_password()
    with open(PROGRAM_PASSWORD_FILE, 'r') as file:
        stored_password = decrypt_text(file.read(), get_key())
    input_password = getpass.getpass("Enter the program password: ")
    return input_password == stored_password

# Function to display passwords in a grid format
def display_passwords(credentials):
    table = Table(title="Credentials")
    table.add_column("No.", style="dim")
    table.add_column("Email/Username", style="dim")
    table.add_column("Website")
    table.add_column("Password", style="bold green")
    for idx, cred in enumerate(sorted(credentials, key=lambda x: x['website']), start=1):
        table.add_row(str(idx), cred['email/uname'], cred['website'], cred['password'])
    console.print(table)

# Function to load and display program info
def display_info():
    if os.path.exists(INFO_FILE):
        with open(INFO_FILE, 'r') as file:
            info = json.load(file)
        console.print("[bold cyan]Program Information:[/bold cyan]")
        console.print("\n---------------------------------------------\n", style="dim")
        console.print(f"Developer: {info.get('developer', 'N/A')}")
        console.print(f"Version: {info.get('version', 'N/A')}")
        console.print(f"Description: {info.get('description', 'N/A')}")
    else:
        console.print("[bold red]Info file not found![/bold red]")

# Function to handle user input with cancel option
def cancel_input(prompt_text):
    def get_input():
        nonlocal input_str
        input_str = input(f"\n{prompt_text} (Type 'CANCEL' to cancel): ")
    
    input_str = None
    input_thread = threading.Thread(target=get_input)
    input_thread.start()
    
    while input_thread.is_alive():
        time.sleep(0.1)
        if input_str == 'CANCEL':
            return None

    return input_str

# Function to check if the script is run with sudo
def check_sudo():
    if os.geteuid() != 0:
        console.print("[bold red]This script must be run with sudo. Exiting...[/bold red]")
        sys.exit(1)

# Function to handle the password manager menu
def password_manager_menu():
    check_sudo()  # Check if the script is run with sudo

    key = get_key()

    if not verify_program_password():
        console.print("[bold red]Invalid program password. Exiting...[/bold red]")
        return

    credentials = load_credentials(key)  # Load credentials on startup

    while True:
        clear_screen()
        console.print("    *********************************************", style="bold cyan")
        console.print("    *                                           *", style="bold cyan")
        console.print("    *           Neo's Password Manager          *", style="bold cyan")
        console.print("    *                                           *", style="bold cyan")
        console.print("    *********************************************", style="bold cyan")
        console.print("\n---------------------------------------------\n", style="dim")

        console.print("[1] Generate Password")
        console.print("[2] List Passwords")
        console.print("[3] Delete Credential")
        console.print("[4] Delete All Credentials")
        console.print("[5] Update")
        console.print("[6] Info")
        console.print("[7] Exit")
        
        console.print("\n---------------------------------------------\n", style="dim")

        option = Prompt.ask("Select an option", choices=['1', '2', '3', '4', '5', '6', '7'])

        if option == '1':
            console.print("\n---------------------------------------------\n", style="dim")
            email_uname = cancel_input("Enter your email/username")
            if email_uname is None:
                continue
            website = cancel_input("Enter the associated website")
            if website is None:
                continue
            password = generate_password()
            credentials.append({'email/uname': email_uname, 'website': website, 'password': password})
            save_credentials(credentials, key)  # Save credentials after generation
            console.print(f"\nGenerated password: [bold green]{password}[/bold green]")
            Prompt.ask("Press Enter to continue...")

        elif option == '2':
            clear_screen()  # Clear the screen before displaying the list
            credentials = load_credentials(key)  # Reload credentials to display the latest
            display_passwords(credentials)
            Prompt.ask("\nPress Enter to continue...")

        elif option == '3':
            if not verify_program_password():
                console.print("[bold red]Invalid program password. Exiting...[/bold red]")
                continue
            clear_screen()
            credentials = load_credentials(key)  # Reload credentials to display the latest
            if credentials:
                # Sort the credentials by website for consistent display and deletion
                sorted_credentials = sorted(credentials, key=lambda x: x['website'])
                display_passwords(sorted_credentials)
                indices_to_delete = cancel_input("\nEnter the numbers of the credentials to delete, separated by commas")
                if indices_to_delete is None:
                    continue
                indices = [int(idx) for idx in indices_to_delete.split(',') if idx.isdigit()]
                # Rebuild the credentials list excluding the selected indices
                credentials = [cred for idx, cred in enumerate(sorted_credentials) if idx + 1 not in indices]
                save_credentials(credentials, key)
                console.print("Selected credentials deleted.")
            else:
                console.print("[bold red]No credentials found.[/bold red]")
            Prompt.ask("\nPress Enter to continue...")

        elif option == '4':
            if not verify_program_password():
                console.print("[bold red]Invalid program password. Exiting...[/bold red]")
                continue
            clear_screen()
            if Prompt.ask("'CANCEL' or confirm the deletion by typing 'CONFIRM'").strip().upper() == 'CONFIRM':
                credentials.clear()
                save_credentials(credentials, key)
                console.print("All credentials deleted.")
            Prompt.ask("\nPress Enter to continue...")

        elif option == '5':  # Update Manager
            clear_screen()
            updater_script_path = os.path.join(SCRIPT_DIR, 'updater.py')
            if os.path.exists(updater_script_path):
                subprocess.run(['python3', updater_script_path])
            else:
                console.print("[bold red]Updater script not found![/bold red]")
            Prompt.ask("\nPress Enter to continue...")

        elif option == '6':  # Info
            clear_screen()
            display_info()
            Prompt.ask("\nPress Enter to continue...")

        elif option == '7':
            console.print("[bold cyan]Exiting Password Manager...[/bold cyan]")
            break

if __name__ == "__main__":
    password_manager_menu()
