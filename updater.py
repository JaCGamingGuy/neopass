import os
import sys
import requests
import json
import shutil
from zipfile import ZipFile
from io import BytesIO
from getpass import getpass
from cryptography.fernet import Fernet

# Define the paths
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_path = '/usr/local/bin/neopass'
update_dir = os.path.join(script_dir, 'neopass_update')
github_repo_url = 'https://github.com/JaCGamingGuy/neopass/archive/refs/heads/main.zip'
credentials_file = os.path.join(script_dir, 'github_credentials.json')
key_file = os.path.join(script_dir, 'encryption_key.key')

# Function to generate or load an encryption key
def get_key():
    if os.path.exists(key_file):
        with open(key_file, 'rb') as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as file:
            file.write(key)
        return key

# Function to encrypt text
def encrypt_text(text, key):
    fernet = Fernet(key)
    return fernet.encrypt(text.encode()).decode()

# Function to decrypt text
def decrypt_text(encrypted_text, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text.encode()).decode()

# Function to save GitHub credentials securely
def save_credentials(username, token):
    key = get_key()
    credentials = {
        'username': encrypt_text(username, key),
        'token': encrypt_text(token, key)
    }
    with open(credentials_file, 'w') as file:
        json.dump(credentials, file)

# Function to load GitHub credentials
def load_credentials():
    if os.path.exists(credentials_file):
        with open(credentials_file, 'r') as file:
            credentials = json.load(file)
        key = get_key()
        return {
            'username': decrypt_text(credentials['username'], key),
            'token': decrypt_text(credentials['token'], key)
        }
    return None

# Check for sudo
def check_sudo():
    if os.geteuid() != 0:
        print("This script requires elevated permissions. Re-launching with sudo...")
        cmd = ['sudo', sys.executable] + sys.argv
        os.execvp(cmd[0], cmd)

# Check for sudo
check_sudo()

# Prompt user for GitHub credentials if not saved
creds = load_credentials()
if creds is None:
    print("GitHub credentials not found.")
    username = input("Enter your GitHub username: ")
    token = getpass("Enter your GitHub personal access token: ")
    save_credentials(username, token)
else:
    username = creds['username']
    token = creds['token']

# Function to download and replace the repository
def download_and_replace_repo():
    print("Downloading the latest version of the repository...")
    try:
        response = requests.get(github_repo_url, auth=(username, token))
        response.raise_for_status()  # Raises HTTPError for bad responses
        if response.status_code == 200:
            # Create/update the update directory
            if not os.path.exists(update_dir):
                os.makedirs(update_dir)

            with ZipFile(BytesIO(response.content)) as zip_file:
                zip_file.extractall(update_dir)

            # Determine the extracted repo path
            extracted_repo_path = os.path.join(update_dir, 'neopass-main')

            if not os.path.exists(extracted_repo_path):
                print(f"Extracted repository path {extracted_repo_path} does not exist.")
                return

            # List of files/directories to exclude from deletion
            exclude_items = {credentials_file, key_file}
            
            # Replace files and directories
            for item in os.listdir(extracted_repo_path):
                s = os.path.join(extracted_repo_path, item)
                d = os.path.join(repo_path, item)
                
                # Skip excluded items
                if os.path.basename(d) in exclude_items:
                    continue

                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    if os.path.exists(d):
                        os.remove(d)
                    shutil.copy2(s, d)

            print("Repository updated successfully.")
        else:
            print(f"Failed to download repository. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during download: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if os.path.exists(update_dir):
            shutil.rmtree(update_dir)

# Download and replace the local repository
download_and_replace_repo()

# Inform the user
print("\nUpdate complete. Press Enter to return to the main menu.")
input()
