# Carrd Automation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CARRD AUTOMATION WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─► Load Configuration
  │   ├─► Read proxies from proxy/proxies.txt
  │   ├─► Read site name from SITE/title.txt
  │   ├─► Read recipient emails from emails.txt
  │   └─► Load processed emails from processed_emails.json
  │
  ├─► Get Temporary Email (Telegram Bot API)
  │   └─► Generate/Request temp email for registration
  │
  ├─► Setup Browser
  │   ├─► Launch Playwright/Chromium
  │   ├─► Configure proxy (if available)
  │   └─► Set headless mode
  │
  ├─► Navigate to Carrd.co
  │   ├─► Go to https://carrd.co/
  │   ├─► Click "Choose Starting Point"
  │   └─► Select Template
  │
  ├─► Add Form Element
  │   ├─► Click "plus" button
  │   └─► Select "Form" option
  │
  ├─► Activate Pro Trial
  │   ├─► Click "Start Pro Free Trial"
  │   ├─► Enter temporary email
  │   ├─► Generate random password
  │   └─► Submit registration
  │
  ├─► Configure Form
  │   ├─► Open form settings
  │   ├─► Add recipient emails
  │   │   ├─► recipient1@example.com
  │   │   ├─► recipient2@example.com
  │   │   └─► recipient3@example.com
  │   └─► Save settings
  │
  ├─► Save & Publish Site
  │   ├─► Click "Publish"
  │   ├─► Enter site name: {title}-{random}
  │   ├─► Confirm publication
  │   └─► Get published URL: https://{name}.carrd.co
  │
  ├─► Send Messages
  │   │
  │   └─► FOR EACH recipient in emails.txt:
  │       │
  │       ├─► Check if already processed
  │       │   └─► Skip if in processed_emails.json
  │       │
  │       ├─► Navigate to published site
  │       │
  │       ├─► Fill Form Fields
  │       │   ├─► Name: {DEFAULT_NAME}
  │       │   ├─► Email: {DEFAULT_EMAIL}
  │       │   └─► Message: {DEFAULT_MESSAGE}
  │       │
  │       ├─► Submit Form
  │       │
  │       ├─► Check Success
  │       │   └─► Look for "Thank you" message
  │       │
  │       ├─► Mark as Processed
  │       │   └─► Add to processed_emails.json
  │       │
  │       └─► Wait (delay between sends)
  │
  ├─► Logging
  │   ├─► Console output (colored)
  │   └─► File: carrd_automation.log
  │
  └─► END

┌─────────────────────────────────────────────────────────────────┐
│                        FILE STRUCTURE                            │
└─────────────────────────────────────────────────────────────────┘

Input Files:
  ├─► proxy/proxies.txt         → Proxy list (optional)
  ├─► SITE/title.txt           → Site name
  └─► emails.txt               → Recipient emails

Output Files:
  ├─► processed_emails.json    → Tracking file
  └─► carrd_automation.log     → Log file

Configuration:
  └─► carrd_automation.py      → Script constants
      ├─► DEFAULT_NAME
      ├─► DEFAULT_EMAIL
      ├─► DEFAULT_MESSAGE
      └─► HEADLESS_MODE

┌─────────────────────────────────────────────────────────────────┐
│                       PROXY FLOW                                 │
└─────────────────────────────────────────────────────────────────┘

Proxy Selection:
  ├─► Load proxies from proxy/proxies.txt
  ├─► Parse formats:
  │   ├─► socks5://user:pass@host:port
  │   ├─► http://user:pass@host:port
  │   └─► https://user:pass@host:port
  ├─► Select random proxy
  └─► Configure browser with proxy

If no proxy:
  └─► Run without proxy (direct connection)

┌─────────────────────────────────────────────────────────────────┐
│                   DUPLICATE PREVENTION                           │
└─────────────────────────────────────────────────────────────────┘

Before Processing Email:
  ├─► Load processed_emails.json
  ├─► Check if email in list
  │   ├─► YES → Skip email
  │   └─► NO → Process email
  │
  └─► After successful send:
      ├─► Add email to processed list
      └─► Save processed_emails.json

To Reset:
  └─► Delete processed_emails.json

┌─────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING                              │
└─────────────────────────────────────────────────────────────────┘

All Steps Include:
  ├─► Try-Catch blocks
  ├─► Fallback selectors
  ├─► Timeout handling
  ├─► Detailed error logging
  └─► Graceful degradation

Example:
  Click "Choose Starting Point"
    ├─► Try: text="Choose Starting Point"
    ├─► Try: a:has-text("Choose Starting Point")
    └─► Try: button:has-text("Choose")

┌─────────────────────────────────────────────────────────────────┐
│                        EXECUTION                                 │
└─────────────────────────────────────────────────────────────────┘

Method 1: Direct Python
  └─► python carrd_automation.py

Method 2: Validation First
  ├─► python validate_config.py
  └─► python carrd_automation.py

Method 3: Launcher Script
  ├─► Linux/Mac: ./run_carrd.sh
  └─► Windows: run_carrd.bat
      ├─► Auto-validates configuration
      ├─► Offers to install dependencies
      └─► Runs automation

┌─────────────────────────────────────────────────────────────────┐
│                     CUSTOMIZATION POINTS                         │
└─────────────────────────────────────────────────────────────────┘

Constants (top of carrd_automation.py):
  ├─► TELEGRAM_BOT_API_KEY    → Telegram API key
  ├─► TELEGRAM_BOT_USERNAME   → Bot username
  ├─► PROXY_FOLDER            → Proxy directory
  ├─► SITE_FOLDER             → Site config directory
  ├─► EMAILS_FILE             → Recipients file
  ├─► HEADLESS_MODE           → Browser visibility
  ├─► DEFAULT_NAME            → Form name field
  ├─► DEFAULT_EMAIL           → Form email field
  └─► DEFAULT_MESSAGE         → Form message field

Methods (can be customized):
  ├─► navigate_and_select_template() → Template selection
  ├─► add_form_element()             → Form creation
  ├─► configure_form_settings()      → Form settings
  └─► send_message_through_form()    → Message sending

```
