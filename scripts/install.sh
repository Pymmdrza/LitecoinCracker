# /bin/bash
# LitecoinCracker Auto Installer

echo "Starting LitecoinCracker installation..."
echo "Cloning LitecoinCracker repository..."
git clone https://github.com/Pymmdrza/LitecoinCracker.git
echo "Navigating to LitecoinCracker directory..."
cd LitecoinCracker || { echo "Failed to enter LitecoinCracker directory"; exit 1; }
echo "Setting execute permissions for install.sh..."
chmod +x install.sh
echo "Requirements installation..."
# check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found, installing pip..."
    # Install pip for Python 3
    if command -v apt-get &> /dev/null
    then
        sudo apt-get update
        sudo apt-get install -y python3-pip
    elif command -v yum &> /dev/null
    then
        sudo yum install -y python3-pip
    else
        echo "Package manager not found. Please install pip manually."
        exit 1
    fi
fi
echo "Installing required Python packages..."
PIP_EXCE="pip3" || PIP_EXCE="pip"
$PIP_EXCE install -r requirements.txt
echo "Installation completed successfully!"
# question to run script now , if y/yes then run script
read -p "Do you want to run LitecoinCracker now? (y/n): "
if [[ $REPLY =~ ^[Yy](es)?$ ]]
then
    echo "Running LitecoinCracker..."
    python3 lite-all.py
else
    echo "You can run LitecoinCracker later by navigating to the LitecoinCracker directory and executing 'python3 lite-all.py'."
fi
echo "Exiting installer."
