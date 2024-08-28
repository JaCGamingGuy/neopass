#!/bin/bash

# Ensure script is run with sudo
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root (with sudo)" 1>&2
    exit 1
fi

# Define target directory
TARGET_DIR="/usr/local/bin/neopass"

# Create the directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Move the files into the target directory
cp password_manager.py requirements.txt info.json "$TARGET_DIR"

# Install required Python packages
pip3 install -r "$TARGET_DIR/requirements.txt"

# Create a shell script to run the Python script with sudo
cat <<EOF > /usr/local/bin/neop
#!/bin/bash
python3 $TARGET_DIR/password_manager.py "\$@"
EOF

# Ensure the shell script is executable
chmod +x /usr/local/bin/neop

echo "Installation complete. You can now run the password manager using the command: neop"
