#!/bin/bash
# This script creates silent placeholder MP3 files
# Replace these with real engine sounds later

sounds=(
    "v8-na"
    "v8-turbo"
    "v8-biturbo"
    "v8-supercharged"
    "v8-hybrid"
    "v10-na"
    "v12-na"
    "v12-turbo"
    "v6-turbo"
    "v6-hybrid"
    "i6-turbo"
    "i4-turbo"
    "i4-na"
    "flat4-turbo"
    "flat6-turbo"
    "w16-turbo"
    "electric"
)

for sound in "${sounds[@]}"; do
    # Create a 5-second silent MP3 using ffmpeg
    ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 5 -q:a 9 -acodec libmp3lame "${sound}.mp3" -y 2>/dev/null
    echo "Created ${sound}.mp3"
done

echo "All placeholder sound files created!"
echo "Replace these with real engine sounds from the sources in README.md"
