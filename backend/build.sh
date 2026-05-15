#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install your Python packages
pip install -r requirements.txt

# 2. Download the full, uncut FFmpeg binary
echo "Downloading full FFmpeg..."
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz

# 3. Move FFmpeg to the backend folder so Python can find it
# Note: Using 'cp' to ensure it's in the right spot regardless of structure
cp ffmpeg-*-amd64-static/ffmpeg ./backend/ffmpeg || cp ffmpeg-*-amd64-static/ffmpeg ./ffmpeg
chmod +x ./backend/ffmpeg || chmod +x ./ffmpeg

# 4. Download the font and put it in the backend folder
echo "Downloading Font..."
wget -O ./backend/font.ttf https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf || wget -O font.ttf https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf

echo "✅ Build script finished successfully"