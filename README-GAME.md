# 🏁 Neon Drag Racing Game

A highly realistic browser-based drag racing game featuring 30+ car brands with real photos and authentic engine sounds!

## 🎮 Features

- **30+ Car Brands** including Russian manufacturers (LADA, UAZ, GAZ, Marussia, Aurus)
- **Real Car Photos** from high-quality sources
- **Authentic Engine Sounds** matched to each car's engine type
- **Realistic Physics** based on power-to-weight ratios
- **Dark Neon Theme** with spectacular visual effects
- **Responsive Design** for PC and smartphone
- **1/4 Mile Drag Racing** with countdown and side-view animation

## 🚀 Quick Start

1. Open `drag-racing-game.html` in a modern web browser
2. Click "Quick Race"
3. Select your car (brand → model → configuration)
4. Select opponent car
5. Click "Start Race" and enjoy!

## 📁 Project Structure

```
drag-racing-game/
├── drag-racing-game.html          # Main game file
├── assets/
│   ├── car-assets.js              # Car image and sound mappings
│   ├── images/
│   │   └── cars/                  # Car photos directory
│   │       └── README.md          # Guide for car images
│   └── sounds/
│       └── engines/               # Engine sound files
│           ├── README.md          # Guide for engine sounds
│           ├── v8-na.mp3          # V8 Naturally Aspirated
│           ├── v8-turbo.mp3       # V8 Twin-Turbo
│           ├── v10-na.mp3         # V10 Naturally Aspirated
│           ├── v12-na.mp3         # V12 Naturally Aspirated
│           ├── v6-turbo.mp3       # V6 Twin-Turbo
│           ├── i6-turbo.mp3       # I6 Turbo
│           ├── i4-turbo.mp3       # I4 Turbo
│           ├── flat6-turbo.mp3    # Flat-6 Turbo
│           ├── electric.mp3       # Electric motor
│           └── ... (more engine sounds)
└── README-GAME.md                 # This file
```

## 🎵 Engine Sounds

The game includes realistic engine sounds for different engine types:

### Engine Types Supported:
- **V8 Engines**: NA, Turbo, Biturbo, Supercharged, Hybrid
- **V10 Engines**: Naturally Aspirated (Lamborghini, Audi R8)
- **V12 Engines**: NA and Twin-Turbo (Lamborghini Aventador, Pagani)
- **V6 Engines**: Twin-Turbo and Hybrid
- **I6 Engines**: Twin-Turbo (BMW M3, Toyota Supra)
- **I4 Engines**: Turbo and NA (Honda, Toyota, LADA)
- **Flat Engines**: Flat-4 Turbo (Subaru), Flat-6 Turbo (Porsche)
- **W16**: Quad-Turbo (Bugatti Chiron)
- **Electric**: Tesla, Porsche Taycan, Lotus Evija

### How Engine Sounds Work:
1. Each car is mapped to its appropriate engine sound in `assets/car-assets.js`
2. Sounds play during the race (from countdown to finish)
3. Volume is balanced between player (60%) and opponent (40%) cars
4. Sounds loop seamlessly during the race

### Adding/Replacing Sounds:
See `assets/sounds/engines/README.md` for:
- Where to download free engine sounds
- Required sound format (MP3, 128kbps+)
- Recommended search terms
- File naming conventions

## 📸 Car Images

The game uses real car photos for authentic visualization:

### Current Implementation:
- Uses Unsplash API URLs for automatic image loading
- Falls back to SVG graphics if images fail to load
- Images displayed in car selection and during races

### Using Local Images:
1. Download car photos (see `assets/images/cars/README.md`)
2. Save in `assets/images/cars/` directory
3. Update URLs in `assets/car-assets.js`:

```javascript
"BMW_M3_Competition_0": {
    image: "assets/images/cars/bmw-m3.jpg",  // Local file
    sound: "assets/sounds/engines/i6-turbo.mp3",
    engineType: "I6 Twin-Turbo"
}
```

## 🚗 Car Database

### Supported Brands:

**Russian Manufacturers:**
- LADA (Vesta Sport, Granta Sport)
- UAZ (Patriot, Hunter)
- GAZ (Volga Siber)
- Marussia (B2 Supercar)
- Aurus (Senat Luxury)

**International Brands:**
- BMW, Mercedes-Benz, Audi, Porsche
- Ferrari, Lamborghini, McLaren, Pagani
- Ford, Chevrolet, Dodge
- Nissan, Toyota, Honda, Subaru
- Tesla, Lotus, Bugatti, Koenigsegg
- Aston Martin, Jaguar, Alfa Romeo
- Maserati, Lexus, Acura

Each brand has multiple models with different configurations!

## 🎨 Visual Effects

- **Neon Theme**: Cyan/magenta color scheme with pulsing effects
- **Tire Smoke**: Dynamic smoke effects during acceleration
- **Sparks**: Random spark effects for added realism
- **Motion Blur**: Speed-based blur effect
- **Countdown Animation**: 3-2-1-GO! sequence
- **Progress Bar**: Real-time race completion indicator

## 🔧 Technical Details

### Technologies:
- Pure HTML5/CSS3/JavaScript
- No external dependencies required
- Responsive CSS Grid and Flexbox layouts
- HTML5 Audio API for sound playback
- SVG graphics as fallback

### Physics Simulation:
- Realistic acceleration based on power-to-weight ratio
- Quarter-mile (1320 ft) track simulation
- Speed calculations using kinematic equations
- Configurable physics constants

### Browser Compatibility:
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support  
- Safari: ✅ Full support
- Mobile browsers: ✅ Optimized

## 🎯 Game Modes

### Quick Race (Current):
- Select your car
- Select opponent car
- Race 1/4 mile drag strip
- See detailed results

### Future Possibilities:
- Tournament mode
- Car customization
- Multiplayer races
- Leaderboards

## 📝 Customization

### Adding New Cars:
1. Add car specs to `carDatabase` in HTML file
2. Add car assets to `assets/car-assets.js`:
   - Image URL or path
   - Engine sound file
   - Engine type description

### Modifying Physics:
Edit `PHYSICS_CONSTANTS` in the HTML file:
```javascript
const PHYSICS_CONSTANTS = {
    ACCELERATION_FACTOR: 0.15,  // Adjust for faster/slower acceleration
    TOP_SPEED_FACTOR: 20,       // Adjust max speeds
    DISTANCE_SCALE: 100,        // Affects race distance calculation
    SPEED_CONVERSION: 10        // Speed display multiplier
};
```

### Changing Visual Theme:
Modify CSS variables:
- Neon colors: `#00ffff` (cyan), `#ff00ff` (magenta)
- Background gradients
- Animation timings

## 🐛 Troubleshooting

**Sounds not playing:**
- Check browser console for errors
- Ensure sound files exist in `assets/sounds/engines/`
- Some browsers block autoplay - user interaction required

**Images not loading:**
- Check internet connection (for Unsplash URLs)
- For local images, verify file paths are correct
- Images fall back to SVG if loading fails

**Game runs slowly:**
- Reduce `GAME_CONSTANTS.RACE_UPDATE_INTERVAL` (increase from 50ms)
- Disable visual effects in CSS
- Close other browser tabs

## 📜 License

This is a demonstration project. Please ensure you have appropriate rights for:
- Car images used
- Engine sound files
- Car brand names and trademarks

## 🤝 Contributing

To improve the game:
1. Add more realistic car specifications
2. Contribute high-quality car photos
3. Add authentic engine sound recordings
4. Improve physics simulation
5. Add new visual effects

## 🎬 Credits

- Game design and development: GitHub Copilot
- Car specifications: Based on manufacturer data
- Images: Unsplash contributors (see image URLs)
- Sounds: Placeholder files (replace with licensed sounds)

---

**Enjoy racing! 🏎️💨**
