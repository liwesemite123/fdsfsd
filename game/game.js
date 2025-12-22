// Game State
const game = {
    state: {
        money: 50000,
        reputation: 0,
        day: 1,
        inventory: [],
        marketListings: [],
        quests: [],
        auctions: [],
        collectorsCorner: [],
        eventActive: null
    },

    // Constants
    GIBDD_BOX_COST: 5000,
    
    // License plate data
    regions: [
        '77', '177', '777', // Moscow
        '78', '178', // Saint Petersburg
        '50', '150', '750', // Moscow region
        '23', '123', // Krasnodar
        '01', '02', '16', '116', '716', // Other regions
        '21', '22', '25', '26', '27', '34', '36', '39',
        '40', '52', '54', '55', '61', '63', '66', '72', '73', '74',
        '86', '90', '93', '95', '96', '97', '98', '99',
        '102', '102', '113', '121', '124', '125', '134', '136',
        '152', '154', '159', '161', '163', '174', '177', '186',
        '190', '196', '197', '199'
    ],

    letters: ['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х'],
    eliteLetters: ['АМР', 'ОМР', 'ЕКХ', 'ССС', 'ТТТ', 'ММР'],
    eliteNumbers: ['001', '007', '111', '222', '333', '444', '555', '666', '777', '888', '999'],

    // Initialize game
    init() {
        this.updateUI();
        this.generateMarketListings();
        this.generateQuests();
        this.generateAuctions();
        this.showNotification('Добро пожаловать на рынок автономеров!', 'success');
        this.startNewsTicker();
    },

    // Generate a random license plate
    generatePlate(forceRarity = null) {
        const rarityRoll = forceRarity || Math.random();
        let plate = {};

        if (rarityRoll > 0.98 || forceRarity === 'historic') {
            // Historic (2%)
            plate = this.generateHistoricPlate();
        } else if (rarityRoll > 0.90 || forceRarity === 'elite') {
            // Elite (8%)
            plate = this.generateElitePlate();
        } else if (rarityRoll > 0.70 || forceRarity === 'nice') {
            // Nice-looking (20%)
            plate = this.generateNicePlate();
        } else {
            // Ordinary (70%)
            plate = this.generateOrdinaryPlate();
        }

        // Generate unique ID using timestamp and counter
        plate.id = `plate-${Date.now()}-${Math.floor(Math.random() * 1000000)}`;
        return plate;
    },

    generateOrdinaryPlate() {
        const letter1 = this.letters[Math.floor(Math.random() * this.letters.length)];
        const letter2 = this.letters[Math.floor(Math.random() * this.letters.length)];
        const letter3 = this.letters[Math.floor(Math.random() * this.letters.length)];
        const number = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
        const region = this.regions[Math.floor(Math.random() * this.regions.length)];

        return {
            number: `${letter1}${number}${letter2}${letter3}`,
            region: region,
            rarity: 'ordinary',
            basePrice: 10000 + Math.floor(Math.random() * 20000)
        };
    },

    generateNicePlate() {
        const patterns = [
            () => {
                // Repeated numbers like 111, 222, etc
                const digit = Math.floor(Math.random() * 10);
                const num = String(digit).repeat(3);
                const letter1 = this.letters[Math.floor(Math.random() * this.letters.length)];
                const letter2 = this.letters[Math.floor(Math.random() * this.letters.length)];
                const letter3 = this.letters[Math.floor(Math.random() * this.letters.length)];
                return `${letter1}${num}${letter2}${letter3}`;
            },
            () => {
                // Same letters
                const letter = this.letters[Math.floor(Math.random() * this.letters.length)];
                const number = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
                return `${letter}${number}${letter}${letter}`;
            }
        ];

        const pattern = patterns[Math.floor(Math.random() * patterns.length)]();
        const region = this.regions[Math.floor(Math.random() * this.regions.length)];

        return {
            number: pattern,
            region: region,
            rarity: 'nice',
            basePrice: 50000 + Math.floor(Math.random() * 100000)
        };
    },

    generateElitePlate() {
        const useEliteLetters = Math.random() > 0.5;
        let number;

        if (useEliteLetters) {
            const eliteLetter = this.eliteLetters[Math.floor(Math.random() * this.eliteLetters.length)];
            const num = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
            number = `${eliteLetter[0]}${num}${eliteLetter[1]}${eliteLetter[2]}`;
        } else {
            const eliteNum = this.eliteNumbers[Math.floor(Math.random() * this.eliteNumbers.length)];
            const letter1 = this.letters[Math.floor(Math.random() * this.letters.length)];
            const letter2 = this.letters[Math.floor(Math.random() * this.letters.length)];
            const letter3 = this.letters[Math.floor(Math.random() * this.letters.length)];
            number = `${letter1}${eliteNum}${letter2}${letter3}`;
        }

        const eliteRegions = ['77', '177', '777', '78', '01'];
        const region = eliteRegions[Math.floor(Math.random() * eliteRegions.length)];

        return {
            number: number,
            region: region,
            rarity: 'elite',
            basePrice: 500000 + Math.floor(Math.random() * 2500000)
        };
    },

    generateHistoricPlate() {
        const styles = ['СССР', 'RUS 90s'];
        const style = styles[Math.floor(Math.random() * styles.length)];
        
        let number;
        if (style === 'СССР') {
            number = `СССР ${String(Math.floor(Math.random() * 10000)).padStart(4, '0')}`;
        } else {
            const letter = this.letters[Math.floor(Math.random() * this.letters.length)];
            number = `${letter}${String(Math.floor(Math.random() * 1000)).padStart(3, '0')} РУС`;
        }

        return {
            number: number,
            region: 'Исторический',
            rarity: 'historic',
            basePrice: 200000 + Math.floor(Math.random() * 800000)
        };
    },

    // Market price with variation
    getMarketPrice(plate, variation = 0.2) {
        const variance = 1 + (Math.random() * variation * 2 - variation);
        return Math.floor(plate.basePrice * variance);
    },

    // Generate market listings
    generateMarketListings() {
        this.state.marketListings = [];
        const count = 8 + Math.floor(Math.random() * 4);
        
        for (let i = 0; i < count; i++) {
            const plate = this.generatePlate();
            plate.price = this.getMarketPrice(plate);
            plate.seller = this.generateNPCName();
            this.state.marketListings.push(plate);
        }
        
        this.renderMarketBoard();
    },

    generateNPCName() {
        const names = [
            'Vasya_777', 'AutoDealer95', 'PlateHunter', 'МихалычГараж',
            'Серёга_Номера', 'DimaTrader', 'КоляПерекуп', 'Andrey_Auto',
            'NomerMaster', 'ГошаГИБДД', 'РоманАвто', 'MaxPlates'
        ];
        return names[Math.floor(Math.random() * names.length)];
    },

    // Render market board
    renderMarketBoard() {
        const container = document.getElementById('market-listings');
        container.innerHTML = '';

        this.state.marketListings.forEach(plate => {
            const card = this.createPlateCard(plate, () => this.buyPlate(plate));
            container.appendChild(card);
        });
    },

    // Create plate card element
    createPlateCard(plate, onBuyClick) {
        const card = document.createElement('div');
        card.className = 'plate-card';
        
        const rarityClass = `rarity-${plate.rarity}`;
        
        card.innerHTML = `
            <div class="plate-number">${plate.number}</div>
            <div class="plate-info">
                <div class="rarity ${rarityClass}">
                    ${this.getRarityLabel(plate.rarity)}
                </div>
                <div>Регион: ${plate.region}</div>
                ${plate.seller ? `<div>Продавец: ${plate.seller}</div>` : ''}
                ${plate.condition ? `<div>Состояние: ${plate.condition}</div>` : ''}
            </div>
            <div class="plate-price">${plate.price.toLocaleString()} ₽</div>
            <button class="action-btn" id="buy-btn-${plate.id}">Купить</button>
        `;
        
        card.querySelector('.action-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            onBuyClick();
        });
        
        return card;
    },

    getRarityLabel(rarity) {
        const labels = {
            'ordinary': '🔵 Обычный',
            'nice': '💙 Красивый',
            'elite': '💛 Элитный',
            'historic': '🟫 Исторический'
        };
        return labels[rarity] || rarity;
    },

    // Buy a plate
    buyPlate(plate) {
        if (this.state.money < plate.price) {
            this.showNotification('Недостаточно денег!', 'error');
            return;
        }

        this.state.money -= plate.price;
        this.state.inventory.push({...plate, purchasePrice: plate.price});
        this.state.marketListings = this.state.marketListings.filter(p => p.id !== plate.id);
        
        this.updateUI();
        this.renderMarketBoard();
        
        if (plate.rarity === 'elite' || plate.rarity === 'historic') {
            this.state.reputation += 5;
            this.showNotification(`Куплен редкий номер! +5 репутации`, 'success');
        } else {
            this.showNotification(`Номер ${plate.number} куплен за ${plate.price.toLocaleString()} ₽`, 'success');
        }
    },

    // Sell a plate
    sellPlate(plate) {
        const salePrice = Math.floor(this.getMarketPrice(plate, 0.3));
        this.state.money += salePrice;
        this.state.inventory = this.state.inventory.filter(p => p.id !== plate.id);
        
        this.updateUI();
        this.showNotification(`Номер продан за ${salePrice.toLocaleString()} ₽`, 'success');
    },

    // GIBDD Box mechanics
    openGIBDDBox() {
        if (this.state.money < this.GIBDD_BOX_COST) {
            this.showNotification('Недостаточно денег для коробки ГИБДД!', 'error');
            return;
        }

        document.getElementById('gibdd-modal').style.display = 'block';
        document.getElementById('box-result').style.display = 'none';
        document.getElementById('box-animation').style.display = 'flex';
    },

    openBox() {
        if (this.state.money < this.GIBDD_BOX_COST) {
            this.showNotification('Недостаточно денег!', 'error');
            return;
        }

        this.state.money -= this.GIBDD_BOX_COST;
        this.updateUI();

        // Show spinning animation
        const boxAnimation = document.getElementById('box-animation');
        const boxResult = document.getElementById('box-result');
        
        boxAnimation.style.display = 'flex';
        boxResult.style.display = 'none';

        // Simulate opening after 2 seconds
        setTimeout(() => {
            const plate = this.generatePlate();
            this.state.inventory.push(plate);
            
            boxAnimation.style.display = 'none';
            boxResult.style.display = 'block';
            
            const rarityClass = `rarity-${plate.rarity}`;
            const isRare = plate.rarity === 'elite' || plate.rarity === 'historic';
            
            boxResult.className = 'box-result';
            if (isRare) {
                boxResult.classList.add('rare-flash');
            }
            
            boxResult.innerHTML = `
                <div class="plate-number ${isRare ? 'price-growth' : ''}">${plate.number}</div>
                <div class="rarity ${rarityClass}">${this.getRarityLabel(plate.rarity)}</div>
                <div>Регион: ${plate.region}</div>
                <div class="plate-price ${isRare ? 'price-growth' : ''}">
                    ~${plate.basePrice.toLocaleString()} ₽
                </div>
            `;
            
            if (isRare) {
                this.state.reputation += 3;
                this.showNotification(`🎉 Редкий номер из коробки! +3 репутации`, 'success');
            } else {
                this.showNotification(`Получен номер ${plate.number}`, 'success');
            }
            
            this.updateUI();
        }, 2000);
    },

    // Marketplace (Avito-style)
    openMarketplace() {
        const modal = document.getElementById('marketplace-modal');
        modal.style.display = 'block';
        
        const container = document.getElementById('marketplace-list');
        container.innerHTML = '';
        
        // Generate marketplace listings
        const listings = [];
        for (let i = 0; i < 6; i++) {
            const plate = this.generatePlate();
            plate.price = this.getMarketPrice(plate, 0.3);
            plate.seller = this.generateNPCName();
            listings.push(plate);
        }
        
        listings.forEach(plate => {
            const card = this.createPlateCard(plate, () => {
                this.buyPlate(plate);
                this.openMarketplace(); // Refresh
            });
            container.appendChild(card);
        });
    },

    // Junkyard
    openJunkyard() {
        const modal = document.getElementById('junkyard-modal');
        modal.style.display = 'block';
        
        const container = document.getElementById('junkyard-list');
        container.innerHTML = '';
        
        // Generate junkyard listings (cheaper, sometimes rare)
        const listings = [];
        for (let i = 0; i < 5; i++) {
            const plate = this.generatePlate();
            plate.price = Math.floor(this.getMarketPrice(plate) * 0.4); // 40% of market price
            plate.condition = Math.random() > 0.7 ? 'Изношенный' : 'Б/У';
            listings.push(plate);
        }
        
        listings.forEach(plate => {
            const card = this.createPlateCard(plate, () => {
                this.buyPlate(plate);
                this.openJunkyard(); // Refresh
            });
            container.appendChild(card);
        });
    },

    // Garage Connections
    openGarageConnections() {
        const modal = document.getElementById('garage-modal');
        modal.style.display = 'block';
        
        const container = document.getElementById('garage-list');
        container.innerHTML = '';
        
        if (this.state.reputation < 10) {
            container.innerHTML = '<p style="text-align: center; color: #ff6b6b;">Требуется репутация 10+ для доступа к редким номерам</p>';
            return;
        }
        
        // Generate rare listings
        const listings = [];
        for (let i = 0; i < 3; i++) {
            const plate = this.generatePlate(Math.random() > 0.5 ? 'elite' : 'nice');
            plate.price = this.getMarketPrice(plate, 0.2);
            plate.seller = this.generateNPCName();
            listings.push(plate);
        }
        
        listings.forEach(plate => {
            const card = this.createPlateCard(plate, () => {
                this.buyPlate(plate);
                this.openGarageConnections(); // Refresh
            });
            container.appendChild(card);
        });
    },

    // Black Market
    openBlackMarket() {
        const modal = document.getElementById('blackmarket-modal');
        modal.style.display = 'block';
        
        const container = document.getElementById('blackmarket-list');
        container.innerHTML = '';
        
        // Generate black market listings (risky)
        const listings = [];
        for (let i = 0; i < 4; i++) {
            const plate = this.generatePlate(Math.random() > 0.3 ? 'elite' : 'historic');
            plate.price = this.getMarketPrice(plate, 0.5);
            plate.seller = '💀 Аноним';
            plate.counterfeit = Math.random() > 0.7; // 30% chance of fake
            listings.push(plate);
        }
        
        listings.forEach(plate => {
            const card = this.createPlateCard(plate, () => {
                if (plate.counterfeit && Math.random() > 0.5) {
                    this.state.money -= plate.price;
                    this.state.reputation -= 10;
                    this.updateUI();
                    this.showNotification('⚠️ ГИБДД конфискует поддельный номер! -10 репутации', 'error');
                } else {
                    this.buyPlate(plate);
                }
                this.openBlackMarket(); // Refresh
            });
            container.appendChild(card);
        });
    },

    // View Inventory
    viewInventory() {
        const modal = document.getElementById('inventory-modal');
        modal.style.display = 'block';
        
        const container = document.getElementById('inventory-list');
        container.innerHTML = '';
        
        if (this.state.inventory.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #00d9ff;">Инвентарь пуст</p>';
            return;
        }
        
        this.state.inventory.forEach(plate => {
            const card = document.createElement('div');
            card.className = 'plate-card';
            
            const rarityClass = `rarity-${plate.rarity}`;
            const marketPrice = this.getMarketPrice(plate, 0.3);
            const profit = marketPrice - (plate.purchasePrice || plate.basePrice);
            
            card.innerHTML = `
                <div class="plate-number">${plate.number}</div>
                <div class="plate-info">
                    <div class="rarity ${rarityClass}">
                        ${this.getRarityLabel(plate.rarity)}
                    </div>
                    <div>Регион: ${plate.region}</div>
                    <div style="color: ${profit > 0 ? '#00ff00' : '#ff6b6b'}">
                        Потенциал: ${profit > 0 ? '+' : ''}${profit.toLocaleString()} ₽
                    </div>
                </div>
                <button class="action-btn" style="background: linear-gradient(135deg, #00aa00 0%, #00ff00 100%);">
                    Продать за ${marketPrice.toLocaleString()} ₽
                </button>
                <button class="action-btn" style="margin-top: 5px; background: linear-gradient(135deg, #aa8800 0%, #ffbb00 100%);">
                    В коллекцию
                </button>
            `;
            
            card.querySelectorAll('.action-btn')[0].addEventListener('click', () => {
                this.sellPlate(plate);
                this.viewInventory(); // Refresh
            });
            
            card.querySelectorAll('.action-btn')[1].addEventListener('click', () => {
                this.addToCollection(plate);
                this.viewInventory(); // Refresh
            });
            
            container.appendChild(card);
        });
    },

    // Work jobs
    workAsMechanic() {
        const earnings = 2000;
        this.state.money += earnings;
        this.advanceDay();
        this.showNotification(`Отработали механиком. +${earnings} ₽`, 'success');
    },

    workAsValet() {
        const earnings = 1500;
        this.state.money += earnings;
        this.advanceDay();
        this.showNotification(`Отработали парковщиком. +${earnings} ₽`, 'success');
    },

    workAsTransporter() {
        const earnings = 3000;
        // Small chance of fine
        if (Math.random() > 0.8) {
            const fine = 1000;
            this.state.money += earnings - fine;
            this.showNotification(`Перевозчик: +${earnings} ₽, штраф камеры -${fine} ₽`, 'warning');
        } else {
            this.state.money += earnings;
            this.showNotification(`Отработали перевозчиком. +${earnings} ₽`, 'success');
        }
        this.advanceDay();
    },

    // Auctions
    viewAuctions() {
        const modal = document.getElementById('auctions-modal');
        modal.style.display = 'block';
        this.renderAuctions();
    },

    generateAuctions() {
        this.state.auctions = [];
        for (let i = 0; i < 3; i++) {
            const plate = this.generatePlate(Math.random() > 0.6 ? 'elite' : 'nice');
            this.state.auctions.push({
                plate: plate,
                currentBid: plate.basePrice,
                timeLeft: 5 + Math.floor(Math.random() * 10),
                bidders: Math.floor(Math.random() * 5)
            });
        }
    },

    renderAuctions() {
        const container = document.getElementById('auctions-list');
        container.innerHTML = '';
        
        this.state.auctions.forEach((auction, index) => {
            const auctionEl = document.createElement('div');
            auctionEl.className = 'auction-item';
            
            const rarityClass = `rarity-${auction.plate.rarity}`;
            
            auctionEl.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="plate-number" style="font-size: 1.2em;">${auction.plate.number}</div>
                        <div class="rarity ${rarityClass}">${this.getRarityLabel(auction.plate.rarity)}</div>
                        <div>Регион: ${auction.plate.region}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="auction-timer">⏰ ${auction.timeLeft} дней</div>
                        <div style="color: #00ff00; font-weight: bold; font-size: 1.1em;">
                            ${auction.currentBid.toLocaleString()} ₽
                        </div>
                        <div style="color: #aaa; font-size: 0.9em;">
                            ${auction.bidders} ставок
                        </div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <input type="number" class="bid-input" placeholder="Ваша ставка" id="bid-${index}">
                    <button class="action-btn" style="width: auto; padding: 8px 20px;">
                        Сделать ставку
                    </button>
                </div>
            `;
            
            auctionEl.querySelector('.action-btn').addEventListener('click', () => {
                const bidInput = document.getElementById(`bid-${index}`);
                const bidAmount = parseInt(bidInput.value, 10);
                
                if (!bidAmount || isNaN(bidAmount) || bidAmount <= auction.currentBid) {
                    this.showNotification('Ставка должна быть выше текущей!', 'error');
                    return;
                }
                
                if (bidAmount > this.state.money) {
                    this.showNotification('Недостаточно денег!', 'error');
                    return;
                }
                
                auction.currentBid = bidAmount;
                auction.bidders++;
                this.showNotification('Ставка сделана!', 'success');
                this.renderAuctions();
            });
            
            container.appendChild(auctionEl);
        });
    },

    // Quests
    generateQuests() {
        this.state.quests = [
            {
                id: 1,
                title: 'Найти номер для чиновника',
                description: 'Найдите номер с регионом 77 и числом 777',
                reward: 50000,
                reputation: 10,
                completed: false,
                check: () => this.state.inventory.some(p => p.region === '77' && p.number.includes('777'))
            },
            {
                id: 2,
                title: 'Первая сделка',
                description: 'Купите и продайте любой номер с прибылью',
                reward: 10000,
                reputation: 5,
                completed: false,
                progress: 0
            },
            {
                id: 3,
                title: 'Коллекционер',
                description: 'Соберите 5 элитных номеров',
                reward: 100000,
                reputation: 20,
                completed: false,
                check: () => this.state.inventory.filter(p => p.rarity === 'elite').length >= 5
            }
        ];
    },

    viewQuests() {
        const modal = document.getElementById('quests-modal');
        modal.style.display = 'block';
        
        const container = document.getElementById('quests-list');
        container.innerHTML = '';
        
        this.state.quests.forEach(quest => {
            const questEl = document.createElement('div');
            questEl.className = `quest-item ${quest.completed ? 'quest-completed' : ''}`;
            
            questEl.innerHTML = `
                <h3>${quest.completed ? '✅' : '📌'} ${quest.title}</h3>
                <p>${quest.description}</p>
                <div class="quest-reward">
                    Награда: ${quest.reward.toLocaleString()} ₽ + ${quest.reputation} репутации
                </div>
                ${quest.completed ? '<p style="color: #00ff00;">Выполнено!</p>' : 
                  '<button class="action-btn">Проверить</button>'}
            `;
            
            if (!quest.completed) {
                questEl.querySelector('.action-btn').addEventListener('click', () => {
                    if (quest.check && quest.check()) {
                        quest.completed = true;
                        this.state.money += quest.reward;
                        this.state.reputation += quest.reputation;
                        this.updateUI();
                        this.showNotification(`Задание выполнено! +${quest.reward} ₽`, 'success');
                        this.viewQuests();
                    } else {
                        this.showNotification('Задание ещё не выполнено', 'warning');
                    }
                });
            }
            
            container.appendChild(questEl);
        });
    },

    // Collector's Corner
    viewCollectorsCorner() {
        const modal = document.getElementById('collectors-modal');
        modal.style.display = 'block';
        
        const container = document.getElementById('collectors-display');
        container.innerHTML = '';
        
        // Show 6 showcase slots
        for (let i = 0; i < 6; i++) {
            const slot = document.createElement('div');
            
            if (this.state.collectorsCorner[i]) {
                const plate = this.state.collectorsCorner[i];
                slot.className = 'showcase-slot showcase-filled';
                const rarityClass = `rarity-${plate.rarity}`;
                slot.innerHTML = `
                    <div class="plate-number" style="font-size: 1.3em;">${plate.number}</div>
                    <div class="rarity ${rarityClass}">${this.getRarityLabel(plate.rarity)}</div>
                    <div style="color: #aaa; font-size: 0.9em;">Регион: ${plate.region}</div>
                `;
            } else {
                slot.className = 'showcase-slot';
                slot.innerHTML = '<div style="color: #666;">Пусто</div>';
            }
            
            container.appendChild(slot);
        }
    },

    addToCollection(plate) {
        if (this.state.collectorsCorner.length >= 6) {
            this.showNotification('Коллекция заполнена!', 'warning');
            return;
        }
        
        this.state.collectorsCorner.push(plate);
        this.state.inventory = this.state.inventory.filter(p => p.id !== plate.id);
        this.state.reputation += 5;
        this.showNotification('Номер добавлен в коллекцию! +5 репутации', 'success');
        this.updateUI();
    },

    // Day progression
    nextDay() {
        this.advanceDay();
        this.generateMarketListings();
        
        // Random events
        if (Math.random() > 0.7) {
            this.triggerRandomEvent();
        }
        
        // Update auctions
        this.state.auctions.forEach(auction => {
            auction.timeLeft--;
            if (auction.timeLeft <= 0) {
                // Auction ended - NPC might win
                if (Math.random() > 0.5) {
                    this.showNotification(`Аукцион завершён. NPC выиграл ${auction.plate.number}`, 'warning');
                }
            }
        });
        
        this.state.auctions = this.state.auctions.filter(a => a.timeLeft > 0);
        if (this.state.auctions.length < 3) {
            this.generateAuctions();
        }
        
        this.showNotification(`День ${this.state.day}. Новые объявления на рынке!`, 'success');
    },

    advanceDay() {
        this.state.day++;
        this.updateUI();
    },

    triggerRandomEvent() {
        const FREE_BOX_DURATION_MS = 60000; // 60 seconds
        
        const events = [
            {
                text: '🚨 Новый закон! Спрос на элитные номера вырос!',
                effect: () => {
                    this.state.marketListings.forEach(p => {
                        if (p.rarity === 'elite') p.price *= 1.5;
                    });
                }
            },
            {
                text: '📰 Рыночный бум! Цены упали на 20%!',
                effect: () => {
                    this.state.marketListings.forEach(p => p.price *= 0.8);
                }
            },
            {
                text: '🎉 Везучий день! Следующая коробка ГИБДД бесплатно!',
                effect: () => {
                    this.GIBDD_BOX_COST = 0;
                    setTimeout(() => { this.GIBDD_BOX_COST = 5000; }, FREE_BOX_DURATION_MS);
                }
            }
        ];
        
        const event = events[Math.floor(Math.random() * events.length)];
        const banner = document.getElementById('event-banner');
        banner.textContent = event.text;
        banner.style.display = 'block';
        event.effect();
        
        setTimeout(() => {
            banner.style.display = 'none';
        }, 10000);
    },

    // News ticker
    startNewsTicker() {
        const news = [
            'Рынок автономеров активен! Найдите свою удачу...',
            'ГИБДД выпускает новые коробки каждый день!',
            'Осторожно с чёрным рынком - много подделок!',
            'Гаражные знакомства требуют репутации...',
            'Элитные номера растут в цене!',
            'Разборка - шанс найти редкие номера дёшево!'
        ];
        
        let currentNews = 0;
        setInterval(() => {
            const ticker = document.getElementById('news-ticker');
            ticker.textContent = '📰 ' + news[currentNews];
            currentNews = (currentNews + 1) % news.length;
        }, 8000);
    },

    // UI Updates
    updateUI() {
        document.getElementById('money').textContent = this.state.money.toLocaleString();
        document.getElementById('reputation').textContent = this.state.reputation;
        document.getElementById('day').textContent = this.state.day;
    },

    // Modal controls
    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    },

    // Notifications
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.style.display = 'block';
        
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
};

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    game.init();
});
