#!/bin/bash
# Carrd Automation Launcher Script
# This script validates the configuration and runs the automation

set -e

echo "================================================"
echo "  Carrd.co Automation Launcher"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 validate_config.py; then
    echo ""
    echo "❌ Configuration validation failed"
    echo ""
    read -p "Do you want to install dependencies now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing dependencies..."
        pip install -r requirements.txt
        echo ""
        echo "Installing Playwright browsers..."
        playwright install chromium
        echo ""
        echo "✓ Dependencies installed"
        echo ""
        echo "Please configure your settings:"
        echo "  1. Add recipient emails to emails.txt"
        echo "  2. (Optional) Add proxies to proxy/proxies.txt"
        echo "  3. Edit SITE/title.txt for your site name"
        echo "  4. Customize message in carrd_automation.py"
        echo ""
        echo "Then run this script again."
        exit 0
    else
        echo "Installation cancelled"
        exit 1
    fi
fi

echo ""
echo "================================================"
echo "  Starting Carrd Automation"
echo "================================================"
echo ""

# Run the automation
python3 carrd_automation.py

echo ""
echo "================================================"
echo "  Automation Complete"
echo "================================================"
echo ""
echo "Check carrd_automation.log for details"
echo "Processed emails are tracked in processed_emails.json"
