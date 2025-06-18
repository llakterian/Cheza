#!/bin/bash

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-pygame git

# Create virtual environment
python3 -m venv cheza_venv
source cheza_venv/bin/activate
python -m pip install -r requirements.txt --user
# Create assets directory
mkdir -p assets sounds

# Generate silent sound files if they don't exist
for sound in move rotate clear gameover; do
    if [ ! -f "sounds/${sound}.wav" ]; then
        ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 0.1 -q:a 9 -acodec libmp3lame "sounds/${sound}.wav"
    fi
done

# Create default icon if missing
if [ ! -f "assets/cheza_icon.png" ]; then
    convert -size 64x64 xc:black -fill red -draw "rectangle 0,0 31,31" -fill blue -draw "rectangle 32,0 63,31" -fill yellow -draw "rectangle 0,32 31,63" -fill green -draw "rectangle 32,32 63,63" assets/cheza_icon.png
fi

# Create launcher
cat > launch_cheza.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source cheza_venv/bin/activate
python3 cheza.py
EOL
chmod +x launch_cheza.sh

# Create desktop shortcut
cat > ~/Desktop/Cheza.desktop << EOL
[Desktop Entry]
Name=Cheza
Comment=Tetris Game for Kids
Exec=$(pwd)/launch_cheza.sh
Icon=$(pwd)/assets/cheza_icon.png
Terminal=false
Type=Application
Categories=Game;
Path=$(pwd)
StartupNotify=true
EOL
chmod +x ~/Desktop/Cheza.desktop

echo "Installation complete! A shortcut has been created on your desktop."