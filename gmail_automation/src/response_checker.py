"""Response checker and notifier"""
import time
from typing import List, Dict
from datetime import datetime


class ResponseChecker:
    """Monitors for new email responses"""
    
    def __init__(self):
        """Initialize response checker"""
        self.last_check_time = time.time()
        self.new_messages: List[Dict] = []
        self.check_interval = 60  # Check every 60 seconds
    
    def check_for_responses(self, gmail_clients: List) -> List[Dict]:
        """
        Check all Gmail accounts for new responses
        
        Args:
            gmail_clients: List of GmailClient instances
            
        Returns:
            List of new messages
        """
        new_messages = []
        
        for client in gmail_clients:
            try:
                messages = client.check_new_messages()
                if messages:
                    new_messages.extend(messages)
                    for msg in messages:
                        self._notify_new_message(msg)
            except Exception as e:
                print(f"⚠️ Ошибка проверки сообщений: {e}")
        
        self.last_check_time = time.time()
        self.new_messages.extend(new_messages)
        
        return new_messages
    
    def _notify_new_message(self, message: Dict):
        """
        Display notification about new message
        
        Args:
            message: Message data
        """
        print("\n" + "="*60)
        print("🔔 НОВОЕ ПИСЬМО!")
        print("="*60)
        print(f"От: {message.get('from', 'Неизвестно')}")
        print(f"Тема: {message.get('subject', 'Без темы')}")
        print(f"Время: {message.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
        print("="*60 + "\n")
        
        # Optionally play a sound or send a desktop notification
        # For simplicity, we just print to console
    
    def should_check(self) -> bool:
        """Check if it's time to check for responses"""
        elapsed = time.time() - self.last_check_time
        return elapsed >= self.check_interval
    
    def get_new_messages_count(self) -> int:
        """Get count of new messages since start"""
        return len(self.new_messages)
