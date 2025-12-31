# Carrd.co Automation Script

Automated script for creating Carrd sites with forms and sending messages through them.

## Features

1. ✅ **Proxy Support**: Connects through proxies (both SOCKS5 and HTTP) from the `proxy/` folder
2. ✅ **Carrd Navigation**: Navigates to https://carrd.co/ and clicks "Choose Starting Point"
3. ✅ **Template Selection**: Selects templates automatically
4. ✅ **Form Creation**: Adds form elements to templates using the "plus" button
5. ✅ **Pro Trial Activation**: Automatically activates "Start Pro Free Trial"
6. ✅ **Email Generation**: Uses Telegram bot API (@anymessage_shop_bot) for temporary emails
7. ✅ **Site Configuration**: Reads site name from `SITE/title.txt`
8. ✅ **Email Recipients**: Manages recipient emails from `emails.txt`
9. ✅ **Message Sending**: Sends messages through the created forms
10. ✅ **Duplicate Prevention**: Tracks processed emails to avoid repetition
11. ✅ **Customizable Fields**: Configure name, email, and message fields in the script

## Directory Structure

```
.
├── carrd_automation.py      # Main automation script
├── proxy/
│   └── proxies.txt          # Proxy list (HTTP/SOCKS5)
├── SITE/
│   └── title.txt           # Site name/title
├── emails.txt              # Recipient email list
├── processed_emails.json   # Tracking file (auto-generated)
└── carrd_automation.log    # Log file (auto-generated)
```

## Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

Or using uv:

```bash
uv pip install playwright python-socks loguru aiohttp
playwright install chromium
```

### 2. Configure Proxies

Add your proxies to `proxy/proxies.txt` (one per line):

```
socks5://user:pass@host:port
http://user:pass@host:port
https://user:pass@host:port
```

### 3. Configure Site Name

Edit `SITE/title.txt` with your desired site name:

```
My Awesome Carrd Site
```

### 4. Add Recipient Emails

Add recipient emails to `emails.txt` (one per line):

```
recipient1@example.com
recipient2@example.com
recipient3@example.com
```

### 5. Customize Message Fields

Edit the script constants at the top of `carrd_automation.py`:

```python
DEFAULT_NAME = "Your Name"
DEFAULT_EMAIL = "your.email@example.com"
DEFAULT_MESSAGE = "Your custom message here"
HEADLESS_MODE = False  # Set to True to run browser in background
```

### 6. Configure Telegram Bot API (Important!)

⚠️ **IMPORTANT**: The Telegram bot API integration is currently a **PLACEHOLDER**.

The script is configured to use `@anymessage_shop_bot` but the actual API implementation needs to be completed. Currently, it generates random temporary emails for testing.

To implement the actual Telegram bot API:
1. Find the correct API endpoint for @anymessage_shop_bot
2. Edit the `get_temporary_email()` method in `carrd_automation.py`
3. Implement the proper API call and response handling

See the comments in the code for details.

## Usage

Run the automation script:

```bash
python carrd_automation.py
```

The script will:
1. Load a random proxy from the proxy folder
2. Navigate to Carrd.co and select a template
3. Add a form to the template
4. Activate Pro trial using Telegram bot API email
5. Configure the form with recipient emails from `emails.txt`
6. Publish the site with the configured name
7. Send messages to all recipients through the form
8. Track processed emails to prevent duplicates

## Configuration

### Telegram Bot API

The script uses the Telegram bot `@anymessage_shop_bot` with API key:
```
CmeCiBaS3fAgAXoGYTYS6l3x2k0Kowyc
```

This is configured in the script and generates temporary emails for account registration.

### Browser Mode

By default, the browser runs in **visible mode** (headless=False) so you can see the automation.

To run in headless mode, edit the script:

```python
browser_options = {
    'headless': True,  # Change to True
    ...
}
```

## Tracking and Prevention of Duplicates

The script maintains a `processed_emails.json` file that tracks all emails that have been sent messages. This ensures:

- ✅ No duplicate messages to the same recipient
- ✅ Can resume from where it left off if interrupted
- ✅ Efficient processing of large email lists

To reset and send to all emails again, simply delete `processed_emails.json`.

## Logs

All activities are logged to:
- Console output (with colors)
- `carrd_automation.log` file

The log file rotates at 10 MB to prevent excessive disk usage.

## Troubleshooting

### Browser Issues

If you encounter browser issues:

```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

### Proxy Issues

- Ensure proxies are in the correct format
- Test proxies manually before adding them
- The script will run without proxy if none are available

### Form Submission Issues

- The script includes waits and delays to handle page loading
- Adjust timeout values if your internet is slow
- Check the log file for detailed error messages

### Email Already Processed

If you need to resend to all emails:

```bash
rm processed_emails.json
```

## Customization

The script is designed to be easily customizable:

1. **Selectors**: Update CSS selectors if Carrd changes their UI
2. **Wait Times**: Adjust `wait_for_timeout()` values for slower connections
3. **Message Content**: Modify `DEFAULT_NAME`, `DEFAULT_EMAIL`, `DEFAULT_MESSAGE`
4. **Template Selection**: Modify `navigate_and_select_template()` to select specific templates

## Notes

⚠️ **Important Notes:**

1. This script automates browser interactions with Carrd.co
2. Make sure you comply with Carrd's Terms of Service
3. The Telegram bot API integration is a placeholder - you may need to adapt it to the actual API
4. Proxy usage helps distribute requests and avoid rate limiting
5. The script tracks processed emails to prevent spam

## License

This is a private project for automation purposes.
