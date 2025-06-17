#!/bin/bash

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-pygame

# Create desktop shortcut
echo "[Desktop Entry]
Name=Cheza
Comment=Tetris Game for Kids
Exec=python3 $PWD/cheza.py
Icon=$PWD/icon.png
Terminal=false
Type=Application
Categories=Game;
StartupNotify=true" > ~/Desktop/Cheza.desktop

chmod +x ~/Desktop/Cheza.desktop

# Make the game executable
chmod +x cheza.py

echo "Installation complete! Double-click the Cheza icon on your desktop to play."