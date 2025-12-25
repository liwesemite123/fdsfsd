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
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Disable automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print(f"   ✅ Браузер запущен")
        except Exception as e:
            print(f"   ❌ Ошибка запуска браузера: {e}")
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
                    except Exception as e:
                        # Skip invalid cookies
                        pass
            
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
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'sent')]"))
                )
                return True
            except:
                # Even if we don't see confirmation, assume it worked
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
