// Car Assets Configuration
// Maps each car to its real image URL and engine sound

const CAR_ASSETS = {
    // BMW Models
    "BMW_M3_Competition_0": {
        image: "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&q=80", // BMW M3
        sound: "assets/sounds/engines/i6-turbo.mp3",
        engineType: "I6 Twin-Turbo"
    },
    "BMW_M3_Competition_1": {
        image: "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&q=80", // BMW M3 CS
        sound: "assets/sounds/engines/i6-turbo.mp3",
        engineType: "I6 Twin-Turbo"
    },
    "BMW_M5_Competition_0": {
        image: "https://images.unsplash.com/photo-1617531653332-bd46c24f2068?w=800&q=80", // BMW M5
        sound: "assets/sounds/engines/v8-turbo.mp3",
        engineType: "V8 Twin-Turbo"
    },
    
    // Mercedes-Benz Models
    "Mercedes-Benz_AMG GT_0": {
        image: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&q=80", // AMG GT
        sound: "assets/sounds/engines/v8-biturbo.mp3",
        engineType: "V8 Biturbo"
    },
    "Mercedes-Benz_AMG GT_1": {
        image: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&q=80", // AMG GT R
        sound: "assets/sounds/engines/v8-biturbo.mp3",
        engineType: "V8 Biturbo"
    },
    "Mercedes-Benz_C63 AMG_0": {
        image: "https://images.unsplash.com/photo-1617531653520-b3d2ba992407?w=800&q=80", // C63 AMG
        sound: "assets/sounds/engines/v8-biturbo.mp3",
        engineType: "V8 Biturbo"
    },
    
    // Audi Models
    "Audi_RS6 Avant_0": {
        image: "https://images.unsplash.com/photo-1610768764270-790fbec18178?w=800&q=80", // RS6 Avant
        sound: "assets/sounds/engines/v8-turbo.mp3",
        engineType: "V8 Twin-Turbo"
    },
    "Audi_R8 V10_0": {
        image: "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800&q=80", // R8 V10
        sound: "assets/sounds/engines/v10-na.mp3",
        engineType: "V10 Naturally Aspirated"
    },
    "Audi_R8 V10_1": {
        image: "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800&q=80", // R8 V10 Performance
        sound: "assets/sounds/engines/v10-na.mp3",
        engineType: "V10 Naturally Aspirated"
    },
    
    // Porsche Models
    "Porsche_911 Turbo S_0": {
        image: "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80", // 911 Turbo S
        sound: "assets/sounds/engines/flat6-turbo.mp3",
        engineType: "Flat-6 Twin-Turbo"
    },
    "Porsche_Taycan Turbo S_0": {
        image: "https://images.unsplash.com/photo-1614165936126-7ff481e92d59?w=800&q=80", // Taycan
        sound: "assets/sounds/engines/electric.mp3",
        engineType: "Electric"
    },
    
    // Ferrari Models
    "Ferrari_F8 Tributo_0": {
        image: "https://images.unsplash.com/photo-1592198084033-aade902d1aae?w=800&q=80", // Ferrari F8
        sound: "assets/sounds/engines/v8-turbo.mp3",
        engineType: "V8 Twin-Turbo"
    },
    "Ferrari_SF90 Stradale_0": {
        image: "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&q=80", // Ferrari SF90
        sound: "assets/sounds/engines/v8-hybrid.mp3",
        engineType: "V8 Hybrid"
    },
    
    // Lamborghini Models
    "Lamborghini_Huracán EVO_0": {
        image: "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&q=80", // Huracan
        sound: "assets/sounds/engines/v10-na.mp3",
        engineType: "V10 Naturally Aspirated"
    },
    "Lamborghini_Aventador SVJ_0": {
        image: "https://images.unsplash.com/photo-1621135802920-133df287f89c?w=800&q=80", // Aventador
        sound: "assets/sounds/engines/v12-na.mp3",
        engineType: "V12 Naturally Aspirated"
    },
    
    // McLaren Models
    "McLaren_720S_0": {
        image: "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&q=80", // McLaren 720S
        sound: "assets/sounds/engines/v8-turbo.mp3",
        engineType: "V8 Twin-Turbo"
    },
    "McLaren_765LT_0": {
        image: "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&q=80", // McLaren 765LT
        sound: "assets/sounds/engines/v8-turbo.mp3",
        engineType: "V8 Twin-Turbo"
    },
    
    // Nissan Models
    "Nissan_GT-R NISMO_0": {
        image: "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=800&q=80", // GT-R
        sound: "assets/sounds/engines/v6-turbo.mp3",
        engineType: "V6 Twin-Turbo"
    },
    "Nissan_Z Performance_0": {
        image: "https://images.unsplash.com/photo-1652509525608-6b44097ea0a9?w=800&q=80", // Nissan Z
        sound: "assets/sounds/engines/v6-turbo.mp3",
        engineType: "V6 Twin-Turbo"
    },
    
    // Toyota Models
    "Toyota_Supra A90_0": {
        image: "https://images.unsplash.com/photo-1617531653332-bd46c24f2068?w=800&q=80", // Supra
        sound: "assets/sounds/engines/i6-turbo.mp3",
        engineType: "I6 Turbo"
    },
    "Toyota_GR Yaris_0": {
        image: "https://images.unsplash.com/photo-1621361365424-06f0e1eb5c49?w=800&q=80", // GR Yaris
        sound: "assets/sounds/engines/i4-turbo.mp3",
        engineType: "I4 Turbo"
    },
    
    // Honda Models
    "Honda_Civic Type R_0": {
        image: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&q=80", // Civic Type R
        sound: "assets/sounds/engines/i4-turbo.mp3",
        engineType: "I4 Turbo"
    },
    "Honda_NSX_0": {
        image: "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=800&q=80", // NSX
        sound: "assets/sounds/engines/v6-hybrid.mp3",
        engineType: "V6 Hybrid"
    },
    
    // Ford Models
    "Ford_Mustang Shelby GT500_0": {
        image: "https://images.unsplash.com/photo-1584345604476-8ec5f5f1e6e5?w=800&q=80", // Mustang GT500
        sound: "assets/sounds/engines/v8-supercharged.mp3",
        engineType: "V8 Supercharged"
    },
    "Ford_GT_0": {
        image: "https://images.unsplash.com/photo-1551830820-330a71b99dcf?w=800&q=80", // Ford GT
        sound: "assets/sounds/engines/v6-turbo.mp3",
        engineType: "V6 Twin-Turbo"
    },
    
    // Chevrolet Models
    "Chevrolet_Corvette Z06_0": {
        image: "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=800&q=80", // Corvette Z06
        sound: "assets/sounds/engines/v8-na.mp3",
        engineType: "V8 Naturally Aspirated"
    },
    "Chevrolet_Camaro ZL1_0": {
        image: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80", // Camaro ZL1
        sound: "assets/sounds/engines/v8-supercharged.mp3",
        engineType: "V8 Supercharged"
    },
    
    // Dodge Models
    "Dodge_Challenger SRT Hellcat_0": {
        image: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80", // Challenger Hellcat
        sound: "assets/sounds/engines/v8-supercharged.mp3",
        engineType: "V8 Supercharged"
    },
    "Dodge_Charger SRT Hellcat_0": {
        image: "https://images.unsplash.com/photo-1563720360172-67b8f3dce741?w=800&q=80", // Charger Hellcat
        sound: "assets/sounds/engines/v8-supercharged.mp3",
        engineType: "V8 Supercharged"
    },
    
    // Tesla Models
    "Tesla_Model S Plaid_0": {
        image: "https://images.unsplash.com/photo-1617788138017-80ad40651399?w=800&q=80", // Model S
        sound: "assets/sounds/engines/electric.mp3",
        engineType: "Electric"
    },
    "Tesla_Model 3 Performance_0": {
        image: "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&q=80", // Model 3
        sound: "assets/sounds/engines/electric.mp3",
        engineType: "Electric"
    },
    
    // LADA Models (Russian)
    "LADA_Vesta Sport_0": {
        image: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80", // LADA Vesta placeholder
        sound: "assets/sounds/engines/i4-na.mp3",
        engineType: "I4 Naturally Aspirated"
    },
    "LADA_Vesta Sport_1": {
        image: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80", // LADA Vesta AMT
        sound: "assets/sounds/engines/i4-na.mp3",
        engineType: "I4 Naturally Aspirated"
    },
    "LADA_Granta Sport_0": {
        image: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80", // LADA Granta
        sound: "assets/sounds/engines/i4-na.mp3",
        engineType: "I4 Naturally Aspirated"
    },
    
    // UAZ Models (Russian)
    "UAZ_Patriot_0": {
        image: "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&q=80", // UAZ Patriot
        sound: "assets/sounds/engines/i4-na.mp3",
        engineType: "I4 Naturally Aspirated"
    },
    "UAZ_Hunter_0": {
        image: "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&q=80", // UAZ Hunter
        sound: "assets/sounds/engines/i4-na.mp3",
        engineType: "I4 Naturally Aspirated"
    },
    
    // GAZ Models (Russian)
    "GAZ_Volga Siber_0": {
        image: "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80", // GAZ Volga
        sound: "assets/sounds/engines/i4-na.mp3",
        engineType: "I4 Naturally Aspirated"
    },
    
    // Marussia Models (Russian)
    "Marussia_B2_0": {
        image: "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80", // Marussia B2
        sound: "assets/sounds/engines/v6-turbo.mp3",
        engineType: "V6 Turbo"
    },
    
    // Aurus Models (Russian)
    "Aurus_Senat_0": {
        image: "https://images.unsplash.com/photo-1563720360172-67b8f3dce741?w=800&q=80", // Aurus Senat
        sound: "assets/sounds/engines/v8-hybrid.mp3",
        engineType: "V8 Hybrid"
    },
    
    // Bugatti Models
    "Bugatti_Chiron_0": {
        image: "https://images.unsplash.com/photo-1566023888-b6f8e87a2753?w=800&q=80", // Bugatti Chiron
        sound: "assets/sounds/engines/w16-turbo.mp3",
        engineType: "W16 Quad-Turbo"
    },
    
    // Koenigsegg Models
    "Koenigsegg_Jesko_0": {
        image: "https://images.unsplash.com/photo-1617531653332-bd46c24f2068?w=800&q=80", // Koenigsegg
        sound: "assets/sounds/engines/v8-turbo.mp3",
        engineType: "V8 Twin-Turbo"
    },
    
    // Pagani Models
    "Pagani_Huayra_0": {
        image: "https://images.unsplash.com/photo-1617531653520-b3d2ba992407?w=800&q=80", // Pagani
        sound: "assets/sounds/engines/v12-turbo.mp3",
        engineType: "V12 Twin-Turbo"
    },
    
    // Aston Martin Models
    "Aston Martin_DBS Superleggera_0": {
        image: "https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800&q=80", // Aston Martin
        sound: "assets/sounds/engines/v12-turbo.mp3",
        engineType: "V12 Twin-Turbo"
    },
    
    // Lotus Models
    "Lotus_Evija_0": {
        image: "https://images.unsplash.com/photo-1600712242805-5f78671b24da?w=800&q=80", // Lotus
        sound: "assets/sounds/engines/electric.mp3",
        engineType: "Electric"
    },
    
    // Maserati Models
    "Maserati_MC20_0": {
        image: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&q=80", // Maserati
        sound: "assets/sounds/engines/v6-turbo.mp3",
        engineType: "V6 Twin-Turbo"
    },
    
    // Alfa Romeo Models
    "Alfa Romeo_Giulia Quadrifoglio_0": {
        image: "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=800&q=80", // Alfa Romeo
        sound: "assets/sounds/engines/v6-turbo.mp3",
        engineType: "V6 Twin-Turbo"
    },
    
    // Jaguar Models
    "Jaguar_F-Type R_0": {
        image: "https://images.unsplash.com/photo-1617531653332-bd46c24f2068?w=800&q=80", // Jaguar
        sound: "assets/sounds/engines/v8-supercharged.mp3",
        engineType: "V8 Supercharged"
    },
    
    // Lexus Models
    "Lexus_LC 500_0": {
        image: "https://images.unsplash.com/photo-1621135802920-133df287f89c?w=800&q=80", // Lexus
        sound: "assets/sounds/engines/v8-na.mp3",
        engineType: "V8 Naturally Aspirated"
    },
    
    // Acura Models
    "Acura_NSX Type S_0": {
        image: "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=800&q=80", // Acura NSX
        sound: "assets/sounds/engines/v6-hybrid.mp3",
        engineType: "V6 Hybrid"
    },
    
    // Subaru Models
    "Subaru_WRX STI_0": {
        image: "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=800&q=80", // Subaru WRX
        sound: "assets/sounds/engines/flat4-turbo.mp3",
        engineType: "Flat-4 Turbo"
    }
};

// Helper function to get car asset key
function getCarAssetKey(brand, model, configIndex) {
    return `${brand}_${model}_${configIndex}`;
}

// Helper function to get car assets
function getCarAssets(brand, model, configIndex) {
    const key = getCarAssetKey(brand, model, configIndex);
    return CAR_ASSETS[key] || {
        image: "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80", // Default sports car
        sound: "assets/sounds/engines/v8-na.mp3",
        engineType: "Unknown"
    };
}
