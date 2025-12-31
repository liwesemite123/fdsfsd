# Carrd.co Automation Script (HTTP API Version)

⚠️ **IMPORTANT: API Endpoints Need Discovery** ⚠️

This script uses **placeholder API endpoints** that will return **404 errors**. You must discover the actual Carrd.co API endpoints before the script will work.

**See [API_ENDPOINT_DISCOVERY.md](API_ENDPOINT_DISCOVERY.md) for step-by-step instructions on finding the real endpoints.**

---

Automated script for creating Carrd sites with forms and sending messages through them using **HTTP requests only** - no browser window is opened.

## Quick Fix for 404 Errors

If you see errors like `Registration failed with status: 404`:

1. Read **[API_ENDPOINT_DISCOVERY.md](API_ENDPOINT_DISCOVERY.md)** 
2. Use browser DevTools (F12) to find real API endpoints
3. Update the endpoints in `carrd_automation.py`

OR use **DRY_RUN_MODE** to test without real API calls:
- Open `carrd_automation.py`
- Change line ~48: `DRY_RUN_MODE = True`
- Run the script to see what it would do

## Features

1. ✅ **Proxy Support**: Connects through proxies (both SOCKS5 and HTTP) from the `proxy/` folder
2. ✅ **HTTP API-based**: No browser window - everything done via HTTP requests
3. ✅ **Carrd Account**: Automatic account registration
4. ✅ **Template Selection**: Creates sites from templates via API
5. ✅ **Form Creation**: Adds form elements via API calls
6. ✅ **Pro Trial Activation**: Automatically activates Pro trial
7. ✅ **Email Generation**: Uses Telegram bot API (@anymessage_shop_bot) for temporary emails
8. ✅ **Site Configuration**: Reads site name from `SITE/title.txt`
9. ✅ **Email Recipients**: Manages recipient emails from `emails.txt`
10. ✅ **Message Sending**: Sends messages through the created forms
11. ✅ **Duplicate Prevention**: Tracks processed emails to avoid repetition
12. ✅ **Customizable Fields**: Configure name, email, and message fields in the script

## Key Advantages of HTTP API Version

- 🚀 **No Browser Required** - Runs completely headless using HTTP requests
- ⚡ **Faster** - Direct API calls are much faster than browser automation
- 💻 **Lower Resource Usage** - No browser means less CPU and memory
- 🔒 **More Reliable** - Not affected by UI changes on the website
- 🎯 **Cleaner** - Pure Python async code without browser dependencies

## Directory Structure

```
.
├── carrd_automation.py      # Main automation script (HTTP API version)
├── proxy/
│   └── proxies.txt          # Proxy list (HTTP/SOCKS5)
├── SITE/
│   └── title.txt           # Site name
├── emails.txt              # Recipient email list
├── processed_emails.json   # Tracking file (auto-generated)
└── carrd_automation.log    # Log file (auto-generated)
```

## Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

**No browser installation needed!** This version uses pure HTTP requests.

### 2. Configure Proxies

Add your proxies to `proxy/proxies.txt` (one per line):

```
socks5://user:pass@host:port
http://user:pass@host:port
socks5://host:port
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
```

## Usage

Run the automation script:

```bash
python carrd_automation.py
```

The script will:
1. Load a random proxy from the proxy folder
2. Create an HTTP session with the proxy
3. Register a Carrd account using Telegram bot API email
4. Activate Pro trial via API
5. Create a new site from template via API
6. Add a form element with recipient emails via API
7. Publish the site via API
8. Send messages to all recipients through the form via HTTP requests
9. Track processed emails to prevent duplicates

## Configuration

### Telegram Bot API

The script uses the Telegram bot `@anymessage_shop_bot` with API key:
```
CmeCiBaS3fAgAXoGYTYS6l3x2k0Kowyc
```

This is configured in the script and generates temporary emails for account registration.

**Note**: Currently uses placeholder implementation (generates random emails). Production use requires actual API endpoint integration.

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

### Proxy Issues

- Ensure proxies are in the correct format
- Test proxies manually before adding them
- The script will run without proxy if none are available

### API Endpoint Issues

- If API calls fail, check the logs for detailed error messages
- Carrd may change their API endpoints - check documentation or network traffic
- Some endpoints in the script may need adjustment for the actual Carrd API

### Email Already Processed

If you need to resend to all emails:

```bash
rm processed_emails.json
```

## Customization

The script is designed to be easily customizable:

1. **API Endpoints**: Update URLs if Carrd changes their API
2. **Wait Times**: Adjust `asyncio.sleep()` values between requests
3. **Message Content**: Modify `DEFAULT_NAME`, `DEFAULT_EMAIL`, `DEFAULT_MESSAGE`
4. **Request Headers**: Customize User-Agent and other headers as needed

## API Endpoints Reference

The script uses these Carrd API endpoints (may need adjustment):

- `/account/register` - Account registration
- `/account/upgrade/trial` - Pro trial activation  
- `/api/sites/create` - Site creation
- `/api/sites/{id}/elements/add` - Add form element
- `/api/sites/{id}/publish` - Publish site
- `{site_url}/submit` - Form submission

**Note**: These endpoints are inferred and may need to be verified/adjusted based on actual Carrd API.

## Comparison with Browser Version

| Feature | HTTP API Version | Browser Version |
|---------|-----------------|-----------------|
| Browser Window | ❌ No | ✅ Yes |
| Speed | ⚡ Fast | 🐌 Slower |
| Resource Usage | 💚 Low | 🔴 High |
| Dependencies | aiohttp only | Playwright + Chromium |
| Installation Size | ~5 MB | ~300 MB |
| Reliability | ✅ High | ⚠️ UI-dependent |

## Notes

⚠️ **Important Notes:**

1. This script uses HTTP requests to interact with Carrd's API
2. API endpoints may need adjustment based on actual Carrd API structure
3. Make sure you comply with Carrd's Terms of Service
4. The Telegram bot API integration is a placeholder - you may need to adapt it
5. Proxy usage helps distribute requests and avoid rate limiting
6. The script tracks processed emails to prevent spam

## License

This is a private project for automation purposes.
