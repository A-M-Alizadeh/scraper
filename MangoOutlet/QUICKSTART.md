# 🚀 Quick Start Guide

## Super Quick Setup (3 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Complete Pipeline
```bash
# Step 1: Collect URLs (2-3 minutes)
python urlScraper.py

# Step 2: Scrape Products (5-10 minutes depending on # of URLs)
python beautifulsoup_scraper.py

# Step 3: Launch Web Interface
python app.py
```

### 3. Open Browser
Visit: `http://localhost:5003`

## 🎯 Best Features to Try

1. **🏆 Best Items Filter**
   - Select "Best Value Score" to see top deals
   - Try "Ultra Steals" for 80%+ discounts under €8

2. **💲 Savings Filters**
   - Sort by "Biggest Savings" to see max euro savings
   - Use "Min Savings" filter to find €20+ savings

3. **🔍 Smart Filtering**
   - Combine filters: Min discount 70% + Max price €10
   - Use "Premium Steals" for high-value items

## 📊 Understanding the Interface

### Product Cards Show:
- **Current Price**: Final price you pay
- **Original Price**: ~~Crossed out~~
- **Discount Badge**: Percentage off
- **Savings Badge**: Euro amount saved
- **Special Badges**: For best items categories

### Sorting Options:
- **Best Value Score**: Algorithm combining discount, savings, and price
- **Ultra Steals**: 80%+ off + under €8
- **Premium Steals**: €30+ original → under €10
- **Best Bang for Buck**: Highest savings ratio

## 🛠️ Troubleshooting

### Common Solutions:
```bash
# If URLs not found:
python urlScraper.py

# If products not found:
python beautifulsoup_scraper.py

# If port busy:
# Change port in app.py: app.run(port=5004)

# Test price extraction:
python test_price_extraction.py
```

## 💡 Pro Tips

1. **Run scrapers overnight** for large datasets
2. **Use filters together** for precise results  
3. **Try different sorting methods** to discover deals
4. **Check "Best Items" section** for curated deals
5. **Bookmark specific filter URLs** for quick access

Happy deal hunting! 🛍️
