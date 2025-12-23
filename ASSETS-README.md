# Game Assets Archives

This directory contains downloadable archives of all game assets for easy distribution and backup.

## Available Archives

### 1. engine-sounds.zip (4.4 KB)
Contains all 17 engine sound MP3 files:
- V8: NA, Turbo, Biturbo, Supercharged, Hybrid
- V10: Naturally Aspirated
- V12: NA and Twin-Turbo
- V6: Turbo and Hybrid
- I6: Twin-Turbo
- I4: Turbo and NA
- Flat-4 and Flat-6: Turbo
- W16: Quad-Turbo
- Electric motor sound

**Note:** These are placeholder files. Replace with real engine recordings from:
- Freesound.org
- Zapsplat.com  
- YouTube Audio Library
- SoundBible.com

### 2. car-images-urls.zip (4.1 KB)
Contains:
- `car-assets.js` - Complete car configuration file with image URLs and sound mappings
- `images/cars/README.md` - Guide for sourcing car photos

**Note:** Image URLs point to Unsplash. To use local images, download photos and update paths in `car-assets.js`.

### 3. game-assets-complete.zip (11 KB)
Complete archive including:
- All engine sound files
- Car assets configuration
- README documentation
- Directory structure

## How to Use

### Extract Archives:
```bash
# Extract engine sounds
unzip engine-sounds.zip

# Extract car images configuration
unzip car-images-urls.zip

# Extract everything
unzip game-assets-complete.zip
```

### Replace Placeholder Sounds:
1. Download real engine sounds from free sources (see README files)
2. Extract engine-sounds.zip
3. Replace the MP3 files with your downloaded sounds
4. Keep the same filenames
5. Ensure format is MP3, 128kbps or higher

### Use Local Car Images:
1. Extract car-images-urls.zip
2. Download car photos (see `assets/images/cars/README.md`)
3. Edit `assets/car-assets.js` to point to local files:
```javascript
"Ferrari_SF90 Stradale_0": {
    image: "assets/images/cars/ferrari-sf90.jpg",  // Local path
    sound: "assets/sounds/engines/v8-hybrid.mp3",
    engineType: "V8 Hybrid"
}
```

## Archive Contents Summary

**Total Files:** 21 asset files
- 17 engine sound MP3 files
- 1 car configuration JavaScript file
- 3 README documentation files

**Total Size:** ~11 KB (placeholder files)

**Real Assets Size (estimated):**
- With real sounds (5-10 sec each): ~2-5 MB
- With local car images (800x600): ~10-20 MB

## Distribution

These archives are perfect for:
- ✅ Sharing the game assets separately
- ✅ Backing up asset configurations
- ✅ Distributing to team members
- ✅ Version control of assets
- ✅ Easy installation/setup

## License & Attribution

**Engine Sounds:**
- Placeholder files are silent/minimal
- When using real sounds, check source licenses
- Recommended sources provide free/CC-licensed sounds
- Some may require attribution

**Car Images:**
- Unsplash URLs: Free to use, no attribution required
- Local images: Ensure you have rights to use
- Manufacturer photos: Check usage terms

## Updates

To create updated archives after modifying assets:

```bash
# Update engine sounds archive
zip -r engine-sounds.zip assets/sounds/engines/*.mp3

# Update car images archive  
zip -r car-images-urls.zip assets/car-assets.js assets/images/

# Update complete archive
zip -r game-assets-complete.zip assets/ -x "*.sh"
```

## Support

For issues with:
- **Sounds not playing:** Check browser console, ensure MP3 format
- **Images not loading:** Verify URLs/paths in `car-assets.js`
- **Archive extraction:** Use unzip, 7-Zip, or WinRAR

See main `README-GAME.md` for complete game documentation.
