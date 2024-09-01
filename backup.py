import os
import zipfile
from datetime import datetime
from rich.console import Console
from rich.table import Table
import subprocess

try:
    import psutil
except ImportError:
    print("psutil module is not installed. Please install it using 'pip install psutil'.")
    exit(1)

# Initialize the rich console
console = Console()

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_TO_BACKUP = [
    'credentials.json',
    'key.key',
    'program_password.txt',
    'github_credentials.json',
    'encryption_key.key'
]

# Function to find connected USB drives
def find_usb_drives():
    usb_drives = []
    try:
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts:
                usb_drives.append(partition.mountpoint)
    except Exception as e:
        console.print(f"[bold red]Error finding USB drives: {e}[/bold red]")
    return usb_drives

# Function to find large block devices
def find_large_block_devices(min_size_gb=6.0):
    large_devices = []
    try:
        # Get block device list
        block_devices = subprocess.check_output(['ls', '/dev/block'], text=True).splitlines()
        for device in block_devices:
            device_path = f'/dev/block/{device}'
            try:
                size_bytes = int(subprocess.check_output(['blockdev', '--getsize64', device_path], text=True).strip())
                size_gb = size_bytes / (1024 ** 3)
                if size_gb >= min_size_gb:
                    large_devices.append((device_path, size_gb))
            except subprocess.CalledProcessError:
                continue
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error while finding large block devices: {e}[/bold red]")

    return large_devices

# Function to create a timestamped zip backup
def create_backup(backup_location):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_zip = os.path.join(backup_location, f'backup_{timestamp}.zip')
    
    with zipfile.ZipFile(backup_zip, 'w') as zipf:
        for file_name in FILES_TO_BACKUP:
            file_path = os.path.join(SCRIPT_DIR, file_name)
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=file_name)
                console.print(f"Added {file_name} to {backup_zip}")
            else:
                console.print(f"[bold red]{file_name} not found, skipping...[/bold red]")
    
    console.print(f"\nBackup created successfully at {backup_zip}")

# Function to select a USB drive
def select_usb_drive():
    usb_drives = find_usb_drives()
    if not usb_drives:
        console.print("[bold red]No USB drives found. Attempting to find large block devices...[/bold red]")
        large_devices = find_large_block_devices()
        if not large_devices:
            console.print("[bold red]No large block devices found. (Error Code: 1)[/bold red]")
            console.print("No USB drives found. Please check your USB connection and try again.")
            return None

        # Display large devices in a table
        table = Table(title="Large Block Devices")
        table.add_column("No.", style="dim")
        table.add_column("Device", style="dim")
        table.add_column("Size (GB)")

        for idx, (device, size) in enumerate(large_devices, start=1):
            table.add_row(str(idx), device, f"{size:.2f}")
        console.print(table)
        
        console.print("\n[bold yellow]Type 'CANCEL', 'q', or 'Q' to abort the selection.[/bold yellow]")

        while True:
            choice = input(f"Select a large block device (1-{len(large_devices)}) or type 'CANCEL', 'q', or 'Q' to abort: ")
            if choice.upper() in ['CANCEL', 'Q', 'Q']:
                console.print("[bold red]Operation cancelled by user.[/bold red]")
                return None
            if choice.isdigit() and 1 <= int(choice) <= len(large_devices):
                selected_device = large_devices[int(choice) - 1][0]
                mount_point = '/mnt'  # Default mount point
                if not os.path.ismount(mount_point):
                    os.makedirs(mount_point, exist_ok=True)
                    subprocess.run(['mount', selected_device, mount_point])
                return mount_point
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

    return usb_drives[0]

if __name__ == "__main__":
    backup_location = select_usb_drive()
    if backup_location:
        create_backup(backup_location)
