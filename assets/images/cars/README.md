# Car Images Directory

This directory is for storing real car model photos.

## Image Requirements:
- Format: JPG or PNG
- Recommended size: 800x600 pixels or higher
- Aspect ratio: 4:3 or 16:9
- Side view preferred for racing visualization
- Professional/promotional photos work best

## Naming Convention:
Images are loaded programmatically from URLs defined in `/assets/car-assets.js`.

The current implementation uses Unsplash URLs as placeholders. To use local images:

1. Download high-quality car photos
2. Save them in this directory
3. Update the URLs in `assets/car-assets.js` to point to local files

Example:
```javascript
"BMW_M3_Competition_0": {
    image: "assets/images/cars/bmw-m3-competition.jpg",  // Local file
    sound: "assets/sounds/engines/i6-turbo.mp3",
    engineType: "I6 Twin-Turbo"
},
```

## Where to Get Car Images:

### Free Stock Photo Sites:
1. **Unsplash** - https://unsplash.com/
   - Search for specific car models
   - Free to use, no attribution required
   - High quality professional photos

2. **Pexels** - https://www.pexels.com/
   - Good selection of car photos
   - Free for commercial use

3. **Pixabay** - https://pixabay.com/
   - Free images and photos
   - No attribution required

### Manufacturer Websites:
- Most car manufacturers have press/media sections
- Often provide high-quality promotional images
- Check usage rights and terms

### Search Tips:
- Use specific model names: "BMW M3 Competition 2023"
- Add keywords: "side view", "profile", "press photo"
- For Russian cars: "LADA Vesta Sport", "UAZ Patriot 2023", "Aurus Senat"

## Recommended Images by Brand:

### Russian Manufacturers:
- **LADA Vesta Sport** - Modern Russian sedan
- **LADA Granta Sport** - Compact Russian car
- **UAZ Patriot** - Russian SUV/off-road vehicle
- **UAZ Hunter** - Classic Russian utility vehicle
- **GAZ Volga Siber** - Russian executive sedan
- **Marussia B2** - Russian supercar (rare)
- **Aurus Senat** - Russian luxury limousine

### International Brands:
- Look for official press photos or professional automotive photography
- Side profile photos work best for the racing visualization
- Ensure photos show the complete car

## License Considerations:
- Verify you have rights to use images
- Keep track of image sources
- Respect photographer attribution requirements
- For commercial use, ensure licenses permit it

## Current Implementation:
The game currently uses Unsplash API URLs which load images dynamically.
These work without downloading, but may be rate-limited.

To switch to local images, download photos and update paths in `car-assets.js`.
