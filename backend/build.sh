#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

# Install FFmpeg for rendering
apt-get update && apt-get install -y ffmpeg