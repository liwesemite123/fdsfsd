"""Gmail client with Selenium browser automation for cookie-based sending"""
import json
import os
import time
from typing import Optional, Dict, List
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class GmailBrowserClient:
    """Gmail client using Selenium with cookies for REAL sending"""
    
    def __init__(self, cookie_file: str, headless: bool = True):
        """
        Initialize Gmail browser client
        
        Args:
            cookie_file: Path to cookie JSON file
            headless: Run browser in headless mode (no visible window)
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium не установлен!\n"
                "Установите: pip install selenium webdriver-manager"
            )
        
        self.cookie_file = cookie_file
        self.headless = headless
        self.driver = None
        self.account_email = None
        
        print(f"🌐 Инициализация браузера для {os.path.basename(cookie_file)}...")
        self._init_browser()
        self._load_cookies()
        self._verify_login()
    
    def _init_browser(self):
        """Initialize Chrome browser"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            
            # Headless mode options - use old headless mode for better stability
            if self.headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
            
            # Critical stability options for renderer timeout fixes
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--single-process')  # Run in single process mode
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-client-side-phishing-detection')
            chrome_options.add_argument('--disable-crash-reporter')
            chrome_options.add_argument('--disable-oopr-debug-crash-dump')
            chrome_options.add_argument('--no-crash-upload')
            chrome_options.add_argument('--disable-low-res-tiling')
            
            # Memory and performance
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--shm-size=2gb')
            
            # Window and display
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # User agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Disable automation detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Preferences
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Try to initialize with latest driver
            print(f"   🔧 Инициализация Chrome WebDriver...")
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as driver_error:
                print(f"   ⚠️ Ошибка с ChromeDriverManager: {driver_error}")
                print(f"   🔄 Попытка использовать системный chromedriver...")
                # Try without webdriver-manager (use system chromedriver)
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set extended timeouts for slow connections
            self.driver.set_page_load_timeout(60)  # Increased from 30
            self.driver.set_script_timeout(60)      # Script timeout
            self.driver.implicitly_wait(15)         # Increased from 10
            
            print(f"   ✅ Браузер запущен")
        except Exception as e:
            print(f"   ❌ Ошибка запуска браузера: {e}")
            print(f"")
            print(f"   💡 Решения:")
            print(f"   1. Установите Chrome/Chromium:")
            print(f"      sudo apt-get update")
            print(f"      sudo apt-get install -y chromium-browser chromium-chromedriver")
            print(f"")
            print(f"   2. Используйте альтернативный метод (SMTP - быстрее и стабильнее):")
            print(f"      python gmail_sender_real.py")
            print(f"")
            print(f"   📖 Подробнее: см. TROUBLESHOOTING.md")
            raise
    
    def _load_cookies(self):
        """Load cookies and navigate to Gmail"""
        try:
            # First visit Gmail to set domain
            self.driver.get('https://mail.google.com')
            time.sleep(2)
            
            # Load cookies from file
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            # Add cookies to browser
            cookies_added = 0
            if isinstance(cookie_data, list):
                for cookie in cookie_data:
                    try:
                        cookie_dict = {
                            'name': cookie.get('name'),
                            'value': cookie.get('value'),
                            'domain': cookie.get('domain', '.google.com'),
                        }
                        # Add optional fields if present
                        if 'path' in cookie:
                            cookie_dict['path'] = cookie['path']
                        if 'secure' in cookie:
                            cookie_dict['secure'] = cookie['secure']
                        
                        self.driver.add_cookie(cookie_dict)
                        cookies_added += 1
                    except Exception as e:
                        # Log specific cookie that failed
                        print(f"   ⚠️ Пропущен cookie {cookie.get('name', 'unknown')}: {e}")
            
            if cookies_added == 0:
                raise Exception("Не удалось загрузить ни одного cookie")
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(3)
            
            print(f"   ✅ Cookies загружены")
        except Exception as e:
            print(f"   ❌ Ошибка загрузки cookies: {e}")
            self.close()
            raise
    
    def _verify_login(self):
        """Verify that cookies worked and we're logged in"""
        try:
            # Check if we're on Gmail inbox
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="navigation"]'))
            )
            
            # Try to get email from page
            try:
                email_elem = self.driver.find_element(By.CSS_SELECTOR, 'div[data-tooltip*="@"]')
                if email_elem:
                    self.account_email = email_elem.get_attribute('data-tooltip')
            except:
                pass
            
            print(f"   ✅ Авторизация успешна")
            if self.account_email:
                print(f"   ✅ Аккаунт: {self.account_email}")
        except TimeoutException:
            print(f"   ❌ Не удалось войти в Gmail с этими cookies")
            print(f"   ❌ Cookies могли устареть или быть неверными")
            self.close()
            raise Exception("Gmail login failed with cookies")
    
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
            
            # Check if email was sent (look for "Message sent" notification)
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'sent') or contains(text(), 'Sent')]"))
                )
                print(f"   ✅ Подтверждение отправки получено")
                return True
            except TimeoutException:
                # No confirmation found - likely failed
                print(f"   ⚠️ Не получено подтверждение отправки")
                # Check if compose dialog is still open (indicates failure)
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"]')
                    print(f"   ❌ Окно compose все еще открыто - отправка не удалась")
                    return False
                except NoSuchElementException:
                    # Dialog closed but no confirmation - assume sent
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
        """Cleanup on deletion"""
        self.close()


def check_selenium_installed() -> bool:
    """Check if Selenium is installed"""
    return SELENIUM_AVAILABLE
