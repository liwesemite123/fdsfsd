# Carrd.co Automation - Quick Start Guide

## Prerequisites

- Python 3.11 or higher
- Internet connection
- Valid proxies (optional but recommended)

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `playwright` - Browser automation framework
- `python-socks` - SOCKS proxy support
- `loguru` - Advanced logging
- `aiohttp` - Async HTTP client

### 2. Install Playwright Browser

```bash
playwright install chromium
```

This downloads the Chromium browser needed for automation.

### 3. Configure Your Setup

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
2. Open a browser and navigate to Carrd.co
3. Select a template and add a form
4. Register with a temporary email
5. Configure the form with your recipient emails
6. Publish the site
7. Send messages to all recipients

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

### "playwright not found"

```bash
pip install playwright
playwright install chromium
```

### "No module named 'loguru'"

```bash
pip install -r requirements.txt
```

### Browser crashes or hangs

- Check your internet connection
- Try running without proxies first
- Increase timeout values in the script

### Form submission fails

- Check that recipient emails are valid
- Ensure the site was published successfully
- Check `carrd_automation.log` for errors

## Advanced Configuration

### Run in Headless Mode

Edit `carrd_automation.py`:

```python
browser_options = {
    'headless': True,  # Change to True
    ...
}
```

### Customize Timeouts

Adjust wait times in the script if you have slow internet:

```python
await page.wait_for_timeout(5000)  # Wait 5 seconds instead of 2
```

### Use Different Templates

Modify the `navigate_and_select_template()` function to select specific templates:

```python
# Select by index
await page.click(f'.template-item:nth-child(3)')

# Select by attribute
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
