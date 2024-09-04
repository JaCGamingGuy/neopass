# Neo Password Manager
(only tested on Debian based system)

-A simple to use CLI based password generator and manager.

-Easily generate, view and delete strong passwords that are stored LOCALLY.

-NeoPass uses AES-128-CBC for encryption and HMAC-SHA256 for authentication.

## What's New

**Backup**

Plug in your external backup of choice, select backup, choose your drive, done.

![Screenshot 2024-09-04 113011](https://github.com/user-attachments/assets/580afab4-6362-43c0-bd89-b8aab24991bc)


## Screenshots

**Main Menu**

![Screenshot 2024-09-04 114535](https://github.com/user-attachments/assets/f5951125-6030-421a-aa16-afcd653d6d04)

**Generation**

![Screenshot 2024-09-04 114421](https://github.com/user-attachments/assets/8af2b49d-b637-456d-b153-4069b80ef2f9)

**List**

![Screenshot 2024-09-04 114225](https://github.com/user-attachments/assets/14145403-0052-4d4b-8edf-7b6aa43d65ac)

**Removal**

![Screenshot 2024-09-04 114759](https://github.com/user-attachments/assets/6d865111-6a5e-4f6a-bb15-5ebac77a8112)

**Bulk-Removal**

![Screenshot 2024-09-04 114856](https://github.com/user-attachments/assets/df070d63-bb8b-4985-95ef-42add4473b69)


## Installation Instructions

**(AIO copy/paste)**

        git clone https://github.com/JaCGamingGuy/neopass.git
        cd neopass
        sudo chmod +x install.sh
        sudo bash ./install.sh
        neop
    
1.  **Clone the Repository**

        git clone https://github.com/JaCGamingGuy/neopass.git

2.  **Navigate to the Cloned Folder**

        cd neopass

3.  **Make the Installation Script Executable**

        chmod +x install.sh

4.  **Run the Installation Script**

        sudo bash ./install.sh
    
6.  **Run the Program**

        neop

## Uninstall Instructions

        cd /usr/local/bin/
        sudo rm -R neopass
        sudo rm neop

***Enjoy***
