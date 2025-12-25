"""Message template handler"""
import os


class MessageTemplate:
    """Handles message text templates"""
    
    def __init__(self, text_file: str):
        """
        Initialize message template
        
        Args:
            text_file: Path to text file containing message template
        """
        self.text_file = text_file
        self.template = ""
        self._load_template()
    
    def _load_template(self):
        """Load message template from file"""
        try:
            if not os.path.exists(self.text_file):
                print(f"⚠️ Файл с текстом не найден: {self.text_file}")
                print(f"⚠️ Используется пустое сообщение")
                return
            
            with open(self.text_file, 'r', encoding='utf-8') as f:
                self.template = f.read()
            
            print(f"✅ Загружен текст сообщения ({len(self.template)} символов)")
        except Exception as e:
            print(f"❌ Ошибка загрузки текста: {e}")
            self.template = ""
    
    def get_message(self, **kwargs) -> str:
        """
        Get message text with optional variable substitution
        
        Args:
            **kwargs: Variables to substitute in template
            
        Returns:
            Formatted message text
        """
        message = self.template
        
        # Simple variable substitution
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            message = message.replace(placeholder, str(value))
        
        return message
    
    def reload(self):
        """Reload template from file"""
        self._load_template()
