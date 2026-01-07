"""Proxy manager for Gmail automation"""
import os
from typing import Optional, List
import random


class ProxyManager:
    """Manages proxy rotation"""
    
    def __init__(self, proxies_file: str):
        """
        Initialize proxy manager
        
        Args:
            proxies_file: Path to file containing proxies (one per line)
                         Format: http://user:pass@host:port or host:port
        """
        self.proxies_file = proxies_file
        self.proxies: List[str] = []
        self.current_index = 0
        self._load_proxies()
    
    def _load_proxies(self):
        """Load proxies from file"""
        try:
            if not os.path.exists(self.proxies_file):
                print(f"⚠️ Файл прокси не найден: {self.proxies_file}")
                print(f"⚠️ Работа без прокси")
                return
            
            with open(self.proxies_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if self.proxies:
                print(f"✅ Загружено {len(self.proxies)} прокси")
            else:
                print(f"⚠️ Файл прокси пуст, работа без прокси")
        except Exception as e:
            print(f"❌ Ошибка загрузки прокси: {e}")
            self.proxies = []
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        # Format proxy if needed
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            proxy = f'http://{proxy}'
        
        return proxy
    
    def get_random_proxy(self) -> Optional[str]:
        """Get random proxy"""
        if not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        
        # Format proxy if needed
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            proxy = f'http://{proxy}'
        
        return proxy
    
    def has_proxies(self) -> bool:
        """Check if proxies are available"""
        return len(self.proxies) > 0
