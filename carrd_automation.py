#!/usr/bin/env python3
"""
Carrd.co Automation Script
This script automates the creation of Carrd sites with forms and sending messages through them.
"""

import asyncio
import random
import string
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, Playwright
from loguru import logger
import aiohttp


# Configuration
TELEGRAM_BOT_API_KEY = "CmeCiBaS3fAgAXoGYTYS6l3x2k0Kowyc"
TELEGRAM_BOT_USERNAME = "anymessage_shop_bot"
PROXY_FOLDER = "proxy"
SITE_FOLDER = "SITE"
EMAILS_FILE = "emails.txt"

# Browser configuration
HEADLESS_MODE = False  # Set to True to run browser in background (no visible window)

# Default form field values (customizable)
DEFAULT_NAME = "John Doe"
DEFAULT_EMAIL = "sender@example.com"
DEFAULT_MESSAGE = "Hello, this is a test message from Carrd form automation."

# Track processed emails to avoid duplicates
PROCESSED_EMAILS_FILE = "processed_emails.json"


class ProxyManager:
    """Manages proxy connections supporting both HTTP and SOCKS5"""
    
    def __init__(self, proxy_folder: str):
        self.proxy_folder = Path(proxy_folder)
        self.proxies: List[Dict[str, str]] = []
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
                    proxy = self._parse_proxy(line)
                    if proxy:
                        self.proxies.append(proxy)
        
        logger.info(f"Loaded {len(self.proxies)} proxies")
    
    def _parse_proxy(self, proxy_str: str) -> Optional[Dict[str, str]]:
        """Parse proxy string into a dictionary"""
        try:
            parsed = urlparse(proxy_str)
            if parsed.scheme in ['http', 'https', 'socks5']:
                return {
                    'server': f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                    'username': parsed.username or '',
                    'password': parsed.password or ''
                }
        except Exception as e:
            logger.error(f"Failed to parse proxy {proxy_str}: {e}")
        return None
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the list"""
        if self.proxies:
            return random.choice(self.proxies)
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
            async with aiohttp.ClientSession() as session:
                # TODO: Replace this with actual Telegram bot API implementation
                # This is a simulated implementation as the actual API might work differently
                # You would need to adapt this to the actual @anymessage_shop_bot API
                logger.warning("Using PLACEHOLDER email generation - implement actual Telegram bot API!")
                logger.info(f"Requesting temporary email from {self.bot_username}")
                
                # For now, generate a random email as placeholder
                # Replace this with actual API call when you have the endpoint
                random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                email = f"temp_{random_id}@tempmail.com"
                logger.info(f"Generated temporary email: {email}")
                return email
                
        except Exception as e:
            logger.error(f"Failed to get temporary email: {e}")
            return None


class CarrdAutomation:
    """Main automation class for Carrd.co"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager(PROXY_FOLDER)
        self.email_generator = TelegramEmailGenerator(TELEGRAM_BOT_API_KEY, TELEGRAM_BOT_USERNAME)
        self.processed_emails = self._load_processed_emails()
        self.carrd_site_url: Optional[str] = None
    
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
        
        # You can add more config files here (e.g., description.txt, etc.)
        
        return config
    
    async def setup_browser(self, playwright: Playwright) -> Browser:
        """Setup browser with optional proxy"""
        proxy = self.proxy_manager.get_random_proxy()
        
        browser_options = {
            'headless': HEADLESS_MODE,  # Configurable via constant at top of file
            'args': ['--disable-blink-features=AutomationControlled']
        }
        
        if proxy:
            logger.info(f"Using proxy: {proxy['server']}")
            browser_options['proxy'] = proxy
        
        browser = await playwright.chromium.launch(**browser_options)
        return browser
    
    async def navigate_and_select_template(self, page: Page):
        """Navigate to Carrd and select a template"""
        logger.info("Navigating to https://carrd.co/")
        await page.goto('https://carrd.co/', wait_until='networkidle')
        
        # Click "Choose Starting Point" button
        logger.info("Clicking 'Choose Starting Point' button")
        try:
            # Try multiple selectors in case the button text varies
            await page.click('text="Choose Starting Point"', timeout=10000)
        except:
            # Alternative selectors
            try:
                await page.click('a:has-text("Choose Starting Point")')
            except:
                await page.click('button:has-text("Choose")')
        
        await page.wait_for_timeout(2000)
        
        # Select the template (you would need to identify the specific template from image2)
        logger.info("Selecting template")
        # This is a placeholder - you'll need to adjust based on actual page structure
        # For now, we'll click the first available template
        try:
            await page.click('.template-item:first-child', timeout=5000)
        except:
            # Try alternative selector
            await page.click('[data-template]', timeout=5000)
        
        await page.wait_for_timeout(2000)
    
    async def add_form_element(self, page: Page):
        """Add a form element to the template"""
        logger.info("Adding form element")
        
        # Click the plus button to add elements
        try:
            await page.click('button[title="Add Element"]', timeout=5000)
        except:
            try:
                await page.click('text="+"', timeout=5000)
            except:
                await page.click('.add-element', timeout=5000)
        
        await page.wait_for_timeout(1000)
        
        # Select "Form" from the menu
        logger.info("Selecting 'Form' option")
        try:
            await page.click('text="Form"', timeout=5000)
        except:
            await page.click('[data-element="form"]', timeout=5000)
        
        await page.wait_for_timeout(2000)
    
    async def activate_pro_trial(self, page: Page, temp_email: str):
        """Activate Pro Free Trial"""
        logger.info("Activating Pro Free Trial")
        
        try:
            # Look for Pro trial button
            await page.click('text="Start Pro Free Trial"', timeout=10000)
            await page.wait_for_timeout(2000)
            
            # Fill in registration form with temporary email
            logger.info(f"Registering with email: {temp_email}")
            await page.fill('input[type="email"]', temp_email)
            
            # Fill in password (generate random password)
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            await page.fill('input[type="password"]', password)
            
            # Submit registration
            await page.click('button[type="submit"]', timeout=5000)
            await page.wait_for_timeout(3000)
            
            logger.info("Pro trial activated successfully")
            
        except Exception as e:
            logger.warning(f"Failed to activate Pro trial (may already be in trial): {e}")
    
    async def configure_form_settings(self, page: Page, recipient_emails: List[str]):
        """Configure form with contact settings and recipient emails"""
        logger.info("Configuring form settings")
        
        try:
            # Open form settings (click on the form element)
            await page.click('.form-element', timeout=5000)
            await page.wait_for_timeout(1000)
            
            # Navigate to settings/recipients section
            try:
                await page.click('text="Settings"', timeout=3000)
            except:
                await page.click('[data-tab="settings"]', timeout=3000)
            
            await page.wait_for_timeout(1000)
            
            # Add recipient emails
            logger.info(f"Adding {len(recipient_emails)} recipient emails")
            for email in recipient_emails:
                try:
                    # Find the recipients input field
                    await page.fill('input[placeholder*="email" i]', email)
                    await page.press('input[placeholder*="email" i]', 'Enter')
                    await page.wait_for_timeout(500)
                    logger.info(f"Added recipient: {email}")
                except Exception as e:
                    logger.warning(f"Failed to add recipient {email}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to configure form settings: {e}")
    
    async def save_site(self, page: Page, site_config: Dict[str, str]):
        """Save the site with configured name"""
        logger.info("Saving site")
        
        try:
            # Click publish/save button
            await page.click('text="Publish"', timeout=5000)
            await page.wait_for_timeout(2000)
            
            # Enter site name
            site_name = site_config.get('title', 'mysite').lower().replace(' ', '-')
            # Generate random suffix to ensure uniqueness
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            full_site_name = f"{site_name}-{random_suffix}"
            
            logger.info(f"Setting site name: {full_site_name}")
            await page.fill('input[name="subdomain"]', full_site_name)
            
            # Confirm/Save
            await page.click('button:has-text("Publish")', timeout=5000)
            await page.wait_for_timeout(3000)
            
            # Get the published site URL
            self.carrd_site_url = f"https://{full_site_name}.carrd.co"
            logger.info(f"Site published at: {self.carrd_site_url}")
            
        except Exception as e:
            logger.error(f"Failed to save site: {e}")
    
    async def send_message_through_form(self, page: Page, recipient_email: str, 
                                       name: str = DEFAULT_NAME,
                                       email: str = DEFAULT_EMAIL,
                                       message: str = DEFAULT_MESSAGE):
        """Send a message through the Carrd form"""
        logger.info(f"Sending message to {recipient_email}")
        
        if not self.carrd_site_url:
            logger.error("No Carrd site URL available")
            return False
        
        try:
            # Navigate to the published site
            await page.goto(self.carrd_site_url, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # Fill in the form
            logger.info("Filling form fields")
            await page.fill('input[name="name"]', name)
            await page.fill('input[name="email"]', email)
            await page.fill('textarea[name="message"]', message)
            
            # Submit the form
            await page.click('button[type="submit"]', timeout=5000)
            await page.wait_for_timeout(3000)
            
            # Check for success message
            try:
                success = await page.is_visible('text="Thank you"', timeout=5000)
                if success:
                    logger.info(f"✓ Message sent successfully to {recipient_email}")
                    return True
            except:
                pass
            
            logger.warning(f"Message may not have been sent to {recipient_email}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send message to {recipient_email}: {e}")
            return False
    
    async def run(self):
        """Main execution flow"""
        logger.info("Starting Carrd automation")
        
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
        
        async with async_playwright() as playwright:
            browser = await self.setup_browser(playwright)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Step 1-3: Navigate and select template
                await self.navigate_and_select_template(page)
                
                # Step 4: Add form element
                await self.add_form_element(page)
                
                # Step 5: Activate Pro Trial
                await self.activate_pro_trial(page, temp_email)
                
                # Step 6-7: Configure form and save site
                await self.configure_form_settings(page, recipient_emails)
                await self.save_site(page, site_config)
                
                # Step 8-11: Send messages to all recipients
                logger.info(f"Sending messages to {len(recipient_emails)} recipients")
                for recipient in recipient_emails:
                    success = await self.send_message_through_form(
                        page, 
                        recipient,
                        name=DEFAULT_NAME,
                        email=DEFAULT_EMAIL,
                        message=DEFAULT_MESSAGE
                    )
                    
                    if success:
                        self.processed_emails.add(recipient)
                        self._save_processed_emails()
                    
                    # Add delay between messages to avoid rate limiting
                    await page.wait_for_timeout(random.randint(3000, 5000))
                
                logger.info("Automation completed successfully")
                
            except Exception as e:
                logger.error(f"Automation failed: {e}")
                raise
            finally:
                await browser.close()


async def main():
    """Entry point"""
    automation = CarrdAutomation()
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
