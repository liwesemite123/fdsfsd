# Carrd.co Automation - Quick Start Guide (HTTP API Version)

## Prerequisites

- Python 3.11 or higher
- Internet connection
- Valid proxies (optional but recommended)

**NO browser installation needed!** This version uses pure HTTP requests.

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `aiohttp` - Async HTTP client for API requests
- `aiohttp-socks` - SOCKS proxy support
- `loguru` - Advanced logging

**That's it!** No browser installation required.

### 2. Configure Your Setup

#### Add Recipient Emails

Edit `emails.txt` and add one email per line:

```
recipient1@example.com
recipient2@example.com
recipient3@example.com
```

#### Set Site Name

Edit `SITE/title.txt` with your desired site name:

```
My Awesome Site
```

#### Add Proxies (Optional)

Edit `proxy/proxies.txt` and add proxies (one per line):

```
socks5://user:pass@host:port
http://user:pass@host:port
```

### 4. Customize Message Content

Edit `carrd_automation.py` and modify these constants:

```python
DEFAULT_NAME = "Your Name"
DEFAULT_EMAIL = "your@email.com"
DEFAULT_MESSAGE = "Your custom message here"
```

## Running the Script

### Validate Configuration

First, check if everything is set up correctly:

```bash
python validate_config.py
```

Fix any issues reported before proceeding.

### Run the Automation

```bash
python carrd_automation.py
```

The script will:
1. Load a random proxy (if configured)
2. Create HTTP session with proxy
3. Register account via API with temporary email
4. Activate Pro trial via API
5. Create site from template via API
6. Add form element with recipients via API
7. Publish the site via API
8. Send messages to all recipients via HTTP requests

**All done via HTTP requests - no browser window opens!**

## Monitoring

### Logs

Check the log file for detailed information:

```bash
tail -f carrd_automation.log
```

### Processed Emails

The script tracks processed emails in `processed_emails.json` to avoid duplicates.

To reset and send to all emails again:

```bash
rm processed_emails.json
```

## Troubleshooting

### "No module named 'aiohttp'" or similar

```bash
pip install -r requirements.txt
```

### API request fails

- Check your internet connection
- Try running without proxies first
- Check logs for detailed error messages
- API endpoints may need adjustment

### Form submission fails

- Check that recipient emails are valid
- Ensure the site was published successfully
- Check `carrd_automation.log` for errors

## Advanced Configuration

### Customize Request Delays

Adjust delays between API requests in the script if needed:

```python
await asyncio.sleep(random.uniform(2, 4))  # Random delay 2-4 seconds
```

### Use Different Templates

Modify the template parameter in `create_site_from_template()`:

```python
payload = {
    'template': 'minimal',  # Change template name
    ...
}
```

### Customize API Endpoints

If Carrd changes their API, update the endpoints in the script:

```python
CARRD_BASE_URL = "https://carrd.co"
CARRD_API_URL = "https://api.carrd.co"
```
await page.click('[data-template="minimal"]')
```

## Tips

1. **Test first**: Run with 1-2 recipient emails first to test
2. **Use proxies**: Helps avoid rate limiting
3. **Monitor logs**: Check `carrd_automation.log` for issues
4. **Backup tracking**: Save `processed_emails.json` before resetting

## Support

For issues or questions, check:
- `CARRD_README.md` for detailed documentation
- Script logs in `carrd_automation.log`
- Playwright documentation: https://playwright.dev/python/

## Safety Notes

⚠️ **Important**:
- Respect Carrd's Terms of Service
- Don't send spam or unsolicited messages
- Use reasonable delays between actions
- Don't abuse the automation

---

**Ready to start?** Run `python validate_config.py` to check your setup!
