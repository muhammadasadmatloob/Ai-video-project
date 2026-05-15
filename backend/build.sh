#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install your Python packages
pip install -r requirements.txt

# 2. Download the full, uncut FFmpeg binary (This bypasses the apt-get error!)
echo "Downloading full FFmpeg..."
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
cp ffmpeg-*-amd64-static/ffmpeg ./ffmpeg
chmod +x ./ffmpeg

# 3. Download a free font (Roboto) so subtitles work on the server
echo "Downloading Font..."
wget -O font.ttf https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf