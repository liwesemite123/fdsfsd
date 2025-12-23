# Engine Sound Files

This directory should contain realistic engine sound files for the drag racing game.

## Required Sound Files:

### V8 Engines
- `v8-na.mp3` - V8 Naturally Aspirated (Corvette Z06, Lexus LC 500)
- `v8-turbo.mp3` - V8 Twin-Turbo (BMW M5, Mercedes AMG GT, Ferrari F8, McLaren 720S, Audi RS6, Koenigsegg)
- `v8-biturbo.mp3` - V8 Biturbo (Mercedes AMG GT, C63)
- `v8-supercharged.mp3` - V8 Supercharged (Ford Mustang GT500, Dodge Hellcat, Camaro ZL1, Jaguar F-Type R)
- `v8-hybrid.mp3` - V8 Hybrid (Ferrari SF90, Aurus Senat)

### V10 Engines
- `v10-na.mp3` - V10 Naturally Aspirated (Audi R8 V10, Lamborghini Huracán)

### V12 Engines
- `v12-na.mp3` - V12 Naturally Aspirated (Lamborghini Aventador)
- `v12-turbo.mp3` - V12 Twin-Turbo (Pagani Huayra, Aston Martin DBS)

### V6 Engines
- `v6-turbo.mp3` - V6 Twin-Turbo (Nissan GT-R, Ford GT, Maserati MC20, Alfa Romeo Giulia, Marussia B2)
- `v6-hybrid.mp3` - V6 Hybrid (Honda NSX, Acura NSX)

### I6 Engines
- `i6-turbo.mp3` - I6 Twin-Turbo (BMW M3, Toyota Supra)

### I4 Engines
- `i4-turbo.mp3` - I4 Turbo (Honda Civic Type R, Toyota GR Yaris)
- `i4-na.mp3` - I4 Naturally Aspirated (LADA models, UAZ, GAZ)

### Flat Engines
- `flat4-turbo.mp3` - Flat-4 Turbo (Subaru WRX STI)
- `flat6-turbo.mp3` - Flat-6 Twin-Turbo (Porsche 911 Turbo S)

### Special Engines
- `w16-turbo.mp3` - W16 Quad-Turbo (Bugatti Chiron)
- `electric.mp3` - Electric Motor (Tesla Model S/3, Porsche Taycan, Lotus Evija)

## Where to Get Sounds:

### Free Sound Resources:
1. **Freesound.org** - https://freesound.org/
   - Search for "car engine", "V8 engine", "supercar sound"
   - Requires free account

2. **YouTube Audio Library** - https://www.youtube.com/audiolibrary
   - Download royalty-free sounds
   - Search for car engine sounds

3. **Zapsplat** - https://www.zapsplat.com/
   - Free sound effects with attribution
   - Good selection of car sounds

4. **SoundBible** - http://soundbible.com/
   - Public domain and Creative Commons sounds

### Recommended Search Terms:
- "V8 engine revving"
- "Supercar acceleration"
- "Drag race engine"
- "Ferrari engine sound"
- "Lamborghini exhaust"
- "Electric motor whine"
- "Turbo spool"

## File Format Requirements:
- Format: MP3
- Bitrate: 128 kbps or higher
- Length: 3-10 seconds
- Should be loopable or long enough for race duration

## Instructions:
1. Download appropriate engine sounds from the resources above
2. Convert to MP3 if needed (use ffmpeg or online converter)
3. Rename files to match the names above
4. Place in this directory

## Example ffmpeg conversion:
```bash
ffmpeg -i input.wav -b:a 128k -ar 44100 v8-na.mp3
```

## License Notes:
- Ensure you have rights to use the sounds
- Check license requirements (attribution, commercial use, etc.)
- Keep track of sound sources for attribution if needed
