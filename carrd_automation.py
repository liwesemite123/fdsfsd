#!/usr/bin/env python3
"""
Carrd.co Automation Script (HTTP API-based version)
This script automates the creation of Carrd sites with forms and sending messages through them using HTTP requests.
No browser window is opened - everything is done via API calls.
"""

import asyncio
import random
import string
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin

from loguru import logger
import aiohttp
from aiohttp_socks import ProxyConnector


# Configuration
TELEGRAM_BOT_API_KEY = "CmeCiBaS3fAgAXoGYTYS6l3x2k0Kowyc"
TELEGRAM_BOT_USERNAME = "anymessage_shop_bot"
PROXY_FOLDER = "proxy"
SITE_FOLDER = "SITE"
EMAILS_FILE = "emails.txt"

# Default form field values (customizable)
DEFAULT_NAME = "John Doe"
DEFAULT_EMAIL = "sender@example.com"
DEFAULT_MESSAGE = "Hello, this is a test message from Carrd form automation."

# Track processed emails to avoid duplicates
PROCESSED_EMAILS_FILE = "processed_emails.json"

# Carrd API endpoints (these may need to be adjusted based on actual API)
CARRD_BASE_URL = "https://carrd.co"
CARRD_API_URL = "https://api.carrd.co"


class ProxyManager:
    """Manages proxy connections supporting both HTTP and SOCKS5"""
    
    def __init__(self, proxy_folder: str):
        self.proxy_folder = Path(proxy_folder)
        self.proxies: List[str] = []
        self._load_proxies()
    
    def _load_proxies(self):
        """Load proxies from the proxy folder"""
        proxy_file = self.proxy_folder / "proxies.txt"
        if not proxy_file.exists():
            logger.warning(f"Proxy file not found: {proxy_file}")
            return
        
        with open(proxy_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.proxies.append(line)
        
        logger.info(f"Loaded {len(self.proxies)} proxies")
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the list"""
        if self.proxies:
            return random.choice(self.proxies)
        return None
    
    def create_connector(self, proxy_url: Optional[str] = None) -> Optional[ProxyConnector]:
        """Create a proxy connector for aiohttp"""
        if proxy_url:
            try:
                return ProxyConnector.from_url(proxy_url)
            except Exception as e:
                logger.error(f"Failed to create proxy connector: {e}")
        return None


class TelegramEmailGenerator:
    """Generates temporary emails using Telegram bot API"""
    
    def __init__(self, api_key: str, bot_username: str):
        self.api_key = api_key
        self.bot_username = bot_username
        self.base_url = f"https://api.telegram.org/bot{api_key}"
    
    async def get_temporary_email(self) -> Optional[str]:
        """Request a temporary email from the Telegram bot
        
        NOTE: This is a PLACEHOLDER implementation!
        The actual @anymessage_shop_bot API integration needs to be implemented.
        
        For production use, you need to:
        1. Find the actual API endpoint for @anymessage_shop_bot
        2. Implement the correct API call format
        3. Handle the response properly
        
        Current implementation generates random temp emails for testing purposes.
        """
        try:
            # TODO: Replace this with actual Telegram bot API implementation
            logger.warning("Using PLACEHOLDER email generation - implement actual Telegram bot API!")
            logger.info(f"Requesting temporary email from {self.bot_username}")
            
            # For now, generate a random email as placeholder
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            email = f"temp_{random_id}@tempmail.com"
            logger.info(f"Generated temporary email: {email}")
            return email
            
        except Exception as e:
            logger.error(f"Failed to get temporary email: {e}")
            return None


class CarrdAPIAutomation:
    """Main automation class for Carrd.co using HTTP API requests"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager(PROXY_FOLDER)
        self.email_generator = TelegramEmailGenerator(TELEGRAM_BOT_API_KEY, TELEGRAM_BOT_USERNAME)
        self.processed_emails = self._load_processed_emails()
        self.carrd_site_url: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.site_id: Optional[str] = None
    
    def _load_processed_emails(self) -> set:
        """Load previously processed emails"""
        if Path(PROCESSED_EMAILS_FILE).exists():
            with open(PROCESSED_EMAILS_FILE, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_processed_emails(self):
        """Save processed emails to file"""
        with open(PROCESSED_EMAILS_FILE, 'w') as f:
            json.dump(list(self.processed_emails), f, indent=2)
    
    def _load_recipient_emails(self) -> List[str]:
        """Load recipient emails from file"""
        emails = []
        if Path(EMAILS_FILE).exists():
            with open(EMAILS_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        emails.append(line)
        
        # Filter out already processed emails
        new_emails = [e for e in emails if e not in self.processed_emails]
        logger.info(f"Loaded {len(new_emails)} unprocessed emails out of {len(emails)} total")
        return new_emails
    
    def _load_site_config(self) -> Dict[str, str]:
        """Load site configuration from SITE folder"""
        config = {}
        site_folder = Path(SITE_FOLDER)
        
        # Load title
        title_file = site_folder / "title.txt"
        if title_file.exists():
            with open(title_file, 'r') as f:
                config['title'] = f.read().strip()
        else:
            config['title'] = "My Carrd Site"
        
        return config
    
    async def create_session(self):
        """Create HTTP session with optional proxy"""
        proxy_url = self.proxy_manager.get_random_proxy()
        
        if proxy_url:
            logger.info(f"Using proxy: {proxy_url}")
            connector = self.proxy_manager.create_connector(proxy_url)
            self.session = aiohttp.ClientSession(connector=connector)
        else:
            logger.info("Running without proxy")
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def register_account(self, temp_email: str) -> bool:
        """Register a new Carrd account via API"""
        logger.info(f"Registering account with email: {temp_email}")
        
        try:
            # Generate random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            
            # Carrd registration endpoint (may need adjustment)
            register_url = f"{CARRD_BASE_URL}/account/register"
            
            payload = {
                'email': temp_email,
                'password': password,
                'password_confirm': password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.post(register_url, data=payload, headers=headers) as response:
                if response.status == 200 or response.status == 302:
                    logger.info("Account registered successfully")
                    # Extract auth token from response or cookies
                    cookies = self.session.cookie_jar.filter_cookies(CARRD_BASE_URL)
                    for cookie in cookies.values():
                        if 'auth' in cookie.key.lower() or 'session' in cookie.key.lower():
                            self.auth_token = cookie.value
                            logger.info("Auth token obtained")
                    return True
                else:
                    logger.error(f"Registration failed with status: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to register account: {e}")
            return False
    
    async def activate_pro_trial(self) -> bool:
        """Activate Pro Free Trial via API"""
        logger.info("Activating Pro Free Trial")
        
        try:
            # Carrd Pro trial endpoint (may need adjustment)
            trial_url = f"{CARRD_BASE_URL}/account/upgrade/trial"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.post(trial_url, headers=headers) as response:
                if response.status == 200 or response.status == 302:
                    logger.info("Pro trial activated successfully")
                    return True
                else:
                    logger.warning(f"Pro trial activation returned status: {response.status}")
                    return False
                    
        except Exception as e:
            logger.warning(f"Failed to activate Pro trial: {e}")
            return False
    
    async def create_site_from_template(self, site_config: Dict[str, str]) -> bool:
        """Create a new site from template via API"""
        logger.info("Creating site from template")
        
        try:
            # Carrd create site endpoint (may need adjustment)
            create_url = f"{CARRD_BASE_URL}/api/sites/create"
            
            site_name = site_config.get('title', 'mysite').lower().replace(' ', '-')
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            full_site_name = f"{site_name}-{random_suffix}"
            
            payload = {
                'template': 'base',  # Default template
                'subdomain': full_site_name,
                'title': site_config.get('title', 'My Site')
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.post(create_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.site_id = data.get('id') or data.get('site_id')
                    self.carrd_site_url = f"https://{full_site_name}.carrd.co"
                    logger.info(f"Site created: {self.carrd_site_url}")
                    return True
                else:
                    logger.error(f"Site creation failed with status: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to create site: {e}")
            return False
    
    async def add_form_to_site(self, recipient_emails: List[str]) -> bool:
        """Add form element to site via API"""
        logger.info("Adding form element to site")
        
        try:
            # Carrd add element endpoint (may need adjustment)
            add_element_url = f"{CARRD_BASE_URL}/api/sites/{self.site_id}/elements/add"
            
            payload = {
                'type': 'form',
                'settings': {
                    'action': 'email',
                    'recipients': recipient_emails,
                    'fields': [
                        {'type': 'text', 'name': 'name', 'label': 'Name', 'required': True},
                        {'type': 'email', 'name': 'email', 'label': 'Email', 'required': True},
                        {'type': 'textarea', 'name': 'message', 'label': 'Message', 'required': True}
                    ]
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.post(add_element_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Form added with {len(recipient_emails)} recipients")
                    return True
                else:
                    logger.error(f"Form addition failed with status: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add form: {e}")
            return False
    
    async def publish_site(self) -> bool:
        """Publish the site via API"""
        logger.info("Publishing site")
        
        try:
            # Carrd publish endpoint (may need adjustment)
            publish_url = f"{CARRD_BASE_URL}/api/sites/{self.site_id}/publish"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.post(publish_url, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Site published at: {self.carrd_site_url}")
                    return True
                else:
                    logger.error(f"Site publishing failed with status: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to publish site: {e}")
            return False
    
    async def send_message_through_form(self, recipient_email: str,
                                       name: str = DEFAULT_NAME,
                                       email: str = DEFAULT_EMAIL,
                                       message: str = DEFAULT_MESSAGE) -> bool:
        """Send a message through the Carrd form via API"""
        logger.info(f"Sending message to {recipient_email}")
        
        if not self.carrd_site_url:
            logger.error("No Carrd site URL available")
            return False
        
        try:
            # Carrd form submission endpoint (typically on the published site)
            form_url = f"{self.carrd_site_url}/submit"
            
            payload = {
                'name': name,
                'email': email,
                'message': message
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': self.carrd_site_url
            }
            
            async with self.session.post(form_url, data=payload, headers=headers) as response:
                if response.status == 200 or response.status == 302:
                    logger.info(f"✓ Message sent successfully to {recipient_email}")
                    return True
                else:
                    logger.warning(f"Message may not have been sent to {recipient_email} (status: {response.status})")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send message to {recipient_email}: {e}")
            return False
    
    async def run(self):
        """Main execution flow"""
        logger.info("Starting Carrd automation (HTTP API mode - no browser window)")
        
        # Load configuration
        site_config = self._load_site_config()
        recipient_emails = self._load_recipient_emails()
        
        if not recipient_emails:
            logger.warning("No unprocessed recipient emails found in emails.txt")
            return
        
        # Get temporary email for registration
        temp_email = await self.email_generator.get_temporary_email()
        if not temp_email:
            logger.error("Failed to get temporary email for registration")
            return
        
        try:
            # Create HTTP session with proxy
            await self.create_session()
            
            # Step 1: Register account
            if not await self.register_account(temp_email):
                logger.error("Failed to register account")
                return
            
            # Step 2: Activate Pro Trial
            await self.activate_pro_trial()
            
            # Step 3: Create site from template
            if not await self.create_site_from_template(site_config):
                logger.error("Failed to create site")
                return
            
            # Step 4: Add form with recipients
            if not await self.add_form_to_site(recipient_emails):
                logger.error("Failed to add form")
                return
            
            # Step 5: Publish site
            if not await self.publish_site():
                logger.error("Failed to publish site")
                return
            
            # Step 6: Send messages to all recipients
            logger.info(f"Sending messages to {len(recipient_emails)} recipients")
            for recipient in recipient_emails:
                success = await self.send_message_through_form(
                    recipient,
                    name=DEFAULT_NAME,
                    email=DEFAULT_EMAIL,
                    message=DEFAULT_MESSAGE
                )
                
                if success:
                    self.processed_emails.add(recipient)
                    self._save_processed_emails()
                
                # Add delay between messages to avoid rate limiting
                await asyncio.sleep(random.uniform(2, 4))
            
            logger.info("Automation completed successfully")
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            raise
        finally:
            await self.close_session()


async def main():
    """Entry point"""
    automation = CarrdAPIAutomation()
    await automation.run()


if __name__ == "__main__":
    # Configure logging
    logger.add("carrd_automation.log", rotation="10 MB")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
