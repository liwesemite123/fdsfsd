# Carrd Automation - Quick Reference Card

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt && playwright install chromium

# 2. Configure
# - Add emails to emails.txt
# - (Optional) Add proxies to proxy/proxies.txt
# - Edit SITE/title.txt

# 3. Run
python carrd_automation.py
```

## 📁 File Locations

| File | Location | Purpose |
|------|----------|---------|
| Recipient emails | `emails.txt` | One email per line |
| Proxies | `proxy/proxies.txt` | One proxy per line |
| Site name | `SITE/title.txt` | Site title/name |
| Main script | `carrd_automation.py` | Automation script |
| Validator | `validate_config.py` | Check setup |
| Logs | `carrd_automation.log` | Runtime logs |
| Tracking | `processed_emails.json` | Processed emails |

## 🔧 Configuration

Edit these constants in `carrd_automation.py`:

```python
# Message customization
DEFAULT_NAME = "Your Name"
DEFAULT_EMAIL = "your@email.com"
DEFAULT_MESSAGE = "Your message"

# Browser mode
HEADLESS_MODE = False  # True = invisible browser
```

## 📝 Proxy Format

```
socks5://username:password@host:port
http://username:password@host:port
https://username:password@host:port
```

## 🔄 Common Tasks

### Validate Configuration
```bash
python validate_config.py
```

### Run Automation
```bash
# Direct
python carrd_automation.py

# With launcher (auto-validates)
./run_carrd.sh         # Linux/Mac
run_carrd.bat          # Windows
```

### Reset Processed Emails
```bash
rm processed_emails.json
```

### View Logs
```bash
tail -f carrd_automation.log
```

## 🎯 Workflow Summary

1. Load config (proxies, emails, site name)
2. Get temp email from Telegram bot
3. Navigate to Carrd.co
4. Select template
5. Add form element
6. Activate Pro trial
7. Configure form with recipients
8. Publish site
9. Send messages to all recipients
10. Track processed emails

## ⚙️ Customization Points

### Change Template Selection
Edit `navigate_and_select_template()` method:
```python
# Select specific template
await page.click('[data-template="minimal"]')
```

### Adjust Timeouts
```python
# Increase for slow connections
await page.wait_for_timeout(5000)  # 5 seconds
```

### Custom Form Fields
Edit `send_message_through_form()` method:
```python
await page.fill('input[name="phone"]', phone_number)
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "playwright not found" | `pip install playwright` |
| "Browser not installed" | `playwright install chromium` |
| Form submission fails | Check logs, verify email format |
| Proxy errors | Test proxy manually, remove bad proxies |
| Already processed | Delete `processed_emails.json` |

## 📚 Documentation

- `CARRD_README.md` - Complete guide
- `QUICKSTART_CARRD.md` - Quick start
- `CONFIG_EXAMPLE.txt` - Examples
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `WORKFLOW.md` - Visual workflow

## 🔐 Security

- ✅ CodeQL scan: 0 alerts
- ✅ No hardcoded secrets in repo
- ✅ Proxy credentials handled securely
- ✅ Input validation on emails

## 💡 Tips

1. **Test first** - Use 1-2 emails to test
2. **Use proxies** - Helps avoid rate limiting
3. **Check logs** - Monitor `carrd_automation.log`
4. **Backup tracking** - Save `processed_emails.json`
5. **Headless mode** - Set `HEADLESS_MODE=True` for production

## 📞 Quick Commands

```bash
# Full setup from scratch
pip install -r requirements.txt
playwright install chromium
python validate_config.py
python carrd_automation.py

# Check what's processed
cat processed_emails.json

# Monitor in real-time
tail -f carrd_automation.log

# Clean start
rm processed_emails.json carrd_automation.log
```

## 🎨 Script Structure

```
carrd_automation.py (460 lines)
├── Configuration (lines 1-30)
├── ProxyManager class (lines 32-70)
├── TelegramEmailGenerator class (lines 72-120)
└── CarrdAutomation class (lines 122-460)
    ├── Configuration loading
    ├── Browser setup
    ├── Navigation & template
    ├── Form creation
    ├── Pro trial activation
    ├── Form configuration
    ├── Site publishing
    └── Message sending
```

---

**Version**: 1.0.0  
**Last Updated**: December 31, 2025  
**Status**: Production Ready ✅
