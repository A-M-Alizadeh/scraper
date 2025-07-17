#!/bin/bash

echo "🛍️ Mango Outlet Scraper Setup Script"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Install requirements
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🚀 Setup complete! You can now run:"
echo "1. python3 urlScraper.py       # Collect product URLs"
echo "2. python3 beautifulsoup_scraper.py  # Scrape product details"
echo "3. python3 app.py              # Launch web interface"
echo ""
echo "Then open http://localhost:5003 in your browser"
echo ""
echo "Happy scraping! 🎉"
