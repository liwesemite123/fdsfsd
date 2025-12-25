"""Gmail client with Selenium browser automation using email/password login"""
import json
import os
import time
from typing import Optional, Dict, List
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class GmailPasswordClient:
    """Gmail client using email/password login with 2FA support"""
    
    def __init__(self, email: str, password: str, backup_email: Optional[str] = None, 
                 twofa_code: Optional[str] = None, headless: bool = True):
        """
        Initialize Gmail client with password authentication
        
        Args:
            email: Gmail email address
            password: Gmail password
            backup_email: Backup email for verification (optional)
            twofa_code: 2FA code from 2fa.online (optional)
            headless: Run browser in headless mode
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium не установлен!\n"
                "Установите: pip install selenium webdriver-manager"
            )
        
        self.email = email
        self.password = password
        self.backup_email = backup_email
        self.twofa_code = twofa_code
        self.headless = headless
        self.driver = None
        
        print(f"🌐 Вход в Gmail: {email}...")
        self._init_browser()
        self._login()
    
    def _init_browser(self):
        """Initialize Chrome browser"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            
            # Headless mode options
            if self.headless:
                chrome_options.add_argument('--headless=new')  # Use new headless mode
            
            # Stability options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-setuid-sandbox')
            
            # Window and display
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # User agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Preferences
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Try to initialize with latest driver
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as driver_error:
                print(f"   ⚠️ Ошибка с ChromeDriverManager: {driver_error}")
                print(f"   🔄 Попытка использовать системный chromedriver...")
                # Try without webdriver-manager (use system chromedriver)
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print(f"   ✅ Браузер запущен")
        except Exception as e:
            print(f"   ❌ Ошибка запуска браузера: {e}")
            print(f"   💡 Убедитесь что Chrome установлен")
            print(f"   💡 Попробуйте: sudo apt-get install chromium-browser chromium-chromedriver")
            print(f"   💡 Или установите Google Chrome")
            raise
    
    def _login(self):
        """Login to Gmail using email/password"""
        try:
            # Navigate to Gmail
            self.driver.get('https://mail.google.com')
            time.sleep(2)
            
            # Enter email
            print(f"   📧 Ввод email...")
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(self.email)
            email_field.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Enter password
            print(f"   🔑 Ввод пароля...")
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Check for backup email verification
            try:
                backup_prompt = self.driver.find_element(By.XPATH, "//*[contains(text(), 'подтверд') or contains(text(), 'verify') or contains(text(), 'email')]")
                if backup_prompt and self.backup_email:
                    print(f"   📧 Запрошена проверка через доп. почту...")
                    backup_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                    backup_field.send_keys(self.backup_email)
                    backup_field.send_keys(Keys.RETURN)
                    time.sleep(3)
            except NoSuchElementException:
                pass
            
            # Check for 2FA
            try:
                twofa_prompt = self.driver.find_element(By.XPATH, "//*[contains(text(), '2-Step') or contains(text(), 'код') or contains(text(), 'code')]")
                if twofa_prompt and self.twofa_code:
                    print(f"   🔐 Получение 2FA кода...")
                    code = self._get_2fa_code()
                    if code:
                        print(f"   🔐 Ввод 2FA кода...")
                        code_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='tel'], input[type='text']")
                        code_field.send_keys(code)
                        code_field.send_keys(Keys.RETURN)
                        time.sleep(3)
            except NoSuchElementException:
                pass
            
            # Verify login success
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="navigation"]'))
            )
            
            print(f"   ✅ Вход выполнен успешно!")
            
        except Exception as e:
            print(f"   ❌ Ошибка входа: {e}")
            self.close()
            raise
    
    def _get_2fa_code(self) -> Optional[str]:
        """Get 2FA code from 2fa.online"""
        try:
            if not self.twofa_code:
                return None
            
            # Open new tab for 2fa.online
            original_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Navigate to 2fa.online
            self.driver.get('https://2fa.online')
            time.sleep(2)
            
            # Enter 2FA secret code
            secret_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            secret_field.send_keys(self.twofa_code)
            time.sleep(1)
            
            # Get generated code
            code_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".token, .code, #token"))
            )
            code = code_element.text.strip()
            
            # Close tab and switch back
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            return code
        except Exception as e:
            print(f"   ⚠️ Ошибка получения 2FA кода: {e}")
            # Switch back to original window
            try:
                self.driver.switch_to.window(original_window)
            except:
                pass
            return None
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email via Gmail web interface
        
        Args:
            to_email: Recipient email
            subject: Email subject  
            body: Email body
            
        Returns:
            True if sent successfully
        """
        try:
            # Click Compose button
            compose_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][gh="cm"]'))
            )
            compose_btn.click()
            time.sleep(1)
            
            # Wait for compose window
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
            )
            
            # Fill in recipient
            to_field = self.driver.find_element(By.CSS_SELECTOR, 'input[name="to"]')
            to_field.send_keys(to_email)
            time.sleep(0.5)
            
            # Fill in subject
            subject_field = self.driver.find_element(By.CSS_SELECTOR, 'input[name="subjectbox"]')
            subject_field.send_keys(subject)
            time.sleep(0.5)
            
            # Fill in body
            body_field = self.driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"][aria-label*="Message"]')
            body_field.send_keys(body)
            time.sleep(0.5)
            
            # Click Send button
            send_btn = self.driver.find_element(By.CSS_SELECTOR, 'div[role="button"][aria-label*="Send"]')
            send_btn.click()
            
            # Wait for send confirmation
            time.sleep(2)
            
            # Check if email was sent
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'sent') or contains(text(), 'Sent')]"))
                )
                print(f"   ✅ Подтверждение отправки получено")
                return True
            except TimeoutException:
                # Check if compose dialog is still open
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"]')
                    print(f"   ❌ Окно compose все еще открыто - отправка не удалась")
                    return False
                except NoSuchElementException:
                    # Dialog closed - assume sent
                    print(f"   ⚠️ Окно закрылось - предполагаем успех")
                    return True
                
        except Exception as e:
            print(f"   ❌ Ошибка отправки: {e}")
            return False
    
    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                print(f"   🔒 Браузер закрыт")
            except:
                pass
    
    def __del__(self):
        """Cleanup"""
        self.close()


def load_accounts_from_file(filepath: str) -> List[Dict]:
    """
    Load accounts from text file
    
    Format:
    GMAIL: email@gmail.com
    PASSWORD: your_password
    DOP MAIL: backup@email.com
    2FA: your_2fa_secret
    ---
    GMAIL: another@gmail.com
    PASSWORD: another_password
    ---
    
    Args:
        filepath: Path to accounts file
        
    Returns:
        List of account dictionaries
    """
    if not os.path.exists(filepath):
        print(f"⚠️ Файл {filepath} не найден")
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        accounts = []
        account_blocks = content.split('---')
        
        for block in account_blocks:
            if not block.strip():
                continue
            
            account = {}
            lines = block.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key == 'GMAIL':
                        account['email'] = value
                    elif key == 'PASSWORD':
                        account['password'] = value
                    elif key == 'DOP MAIL':
                        account['backup_email'] = value
                    elif key == '2FA':
                        account['twofa_code'] = value
            
            if 'email' in account and 'password' in account:
                accounts.append(account)
        
        if accounts:
            print(f"✅ Загружено {len(accounts)} аккаунтов из {filepath}")
            for acc in accounts:
                print(f"   - {acc['email']}")
        
        return accounts
    except Exception as e:
        print(f"❌ Ошибка загрузки {filepath}: {e}")
        return []


def check_selenium_installed() -> bool:
    """Check if Selenium is installed"""
    return SELENIUM_AVAILABLE
