#!/bin/bash

# Get absolute path to game directory
GAME_DIR=$(cd "$(dirname "$0")" && pwd)

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-pygame git

# Create assets and sounds directories
mkdir -p "$GAME_DIR/assets"
mkdir -p "$GAME_DIR/sounds"

# Create launcher script
echo '#!/bin/bash
cd "$(dirname "$0")"
python3 cheza.py' > "$GAME_DIR/launch_cheza.sh"
chmod +x "$GAME_DIR/launch_cheza.sh"

# Create desktop shortcut
echo "[Desktop Entry]
Name=Cheza
Comment=Ultimate Tetris Experience
Exec=\"$GAME_DIR/launch_cheza.sh\"
Icon=$GAME_DIR/assets/cheza_icon.png
Terminal=false
Type=Application
Categories=Game;
Path=$GAME_DIR
StartupNotify=true" > ~/Desktop/Cheza.desktop

chmod +x ~/Desktop/Cheza.desktop

echo "Installation complete! Double-click the Cheza icon on your desktop to play."