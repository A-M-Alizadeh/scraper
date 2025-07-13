import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
import brotli
import re

def scrape_product_details():
    base_url = "https://www.mangooutlet.com"
    urls_file = "urls.json"
    products_file = "products.json"
    
    # Check if urls.json exists
    if not os.path.exists(urls_file):
        print(f"Error: {urls_file} not found. Run the URL collector first.")
        return
    
    # Load URLs from the JSON file
    try:
        with open(urls_file, "r", encoding='utf-8') as f:
            urls = json.load(f)
        print(f"Loaded {len(urls)} URLs to scrape")
    except Exception as e:
        print(f"Error loading URLs: {e}")
        return
    
    # Initialize products file
    products = []
    
    # Setup session with headers to mimic a browser
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    def extract_product_data(soup, url):
        """Extract product details from the BeautifulSoup object"""
        try:
            # Extract product name from H1
            name = ""
            h1_element = soup.find('h1')
            if h1_element:
                name = h1_element.get_text().strip()
            
            # Extract prices using regex patterns from page text
            current_price = ""
            original_price = ""
            page_text = soup.get_text()
            
            # Find all Euro prices in the format €XX,XX
            euro_prices = re.findall(r'€\s*(\d+[.,]\d+)', page_text)
            
            if len(euro_prices) >= 2:
                # Convert to float for comparison
                prices = []
                for price_str in euro_prices[:3]:  # Take first 3 prices
                    try:
                        price_val = float(price_str.replace(',', '.'))
                        formatted_price = f"€{price_str}"
                        prices.append((price_val, formatted_price))
                    except:
                        continue
                
                if len(prices) >= 2:
                    # Sort by value - lowest should be current price
                    prices.sort(key=lambda x: x[0])
                    current_price = prices[0][1]  # Lowest price
                    original_price = prices[-1][1]  # Highest price
            elif len(euro_prices) == 1:
                current_price = f"€{euro_prices[0]}"
            
            # Extract discount percentage
            discount_amount = ""
            discount_match = re.search(r'-(\d+)%', page_text)
            if discount_match:
                discount_amount = f"-{discount_match.group(1)}%"
            
            # Extract main product image
            image_url = ""
            images = soup.find_all('img')
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src and '/fotos/' in src and not any(x in src for x in ['outfit', '_R']):
                    # Get the main product image (not outfit or back view)
                    if src.startswith('//'):
                        image_url = 'https:' + src
                    elif src.startswith('/'):
                        image_url = base_url + src
                    elif src.startswith('http'):
                        image_url = src
                    break
            
            return {
                "name": name,
                "current_price": current_price,
                "original_price": original_price,
                "discount_amount": discount_amount,
                "image_url": image_url,
                "product_url": url,
                "scraped_at": time.time()
            }
            
        except Exception as e:
            print(f"Error extracting data from {url}: {e}")
            return None
    
    total_urls = len(urls)
    
    for i, url in enumerate(urls, 1):
        try:
            full_url = base_url + url
            print(f"Scraping {i}/{total_urls}: {full_url}")
            
            # Make the request
            response = session.get(full_url, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product data
            product_data = extract_product_data(soup, url)
            
            if product_data and product_data['name']:
                products.append(product_data)
                print(f"✓ Extracted: {product_data['name'][:50]}... - {product_data['current_price']}")
                
                # Save progress after each product
                with open(products_file, "w", encoding='utf-8') as f:
                    json.dump(products, f, indent=4, ensure_ascii=False)
            else:
                print(f"✗ Failed to extract data from {url}")
                # Still save the attempt for debugging
                if product_data:
                    products.append(product_data)
                    with open(products_file, "w", encoding='utf-8') as f:
                        json.dump(products, f, indent=4, ensure_ascii=False)
            
            # Small delay between requests to be respectful
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue
    
    print(f"\nScraping completed! Extracted {len(products)} products and saved to {products_file}")
    
    # Print summary
    successful_scrapes = sum(1 for p in products if p.get('name'))
    print(f"Successfully extracted product details for {successful_scrapes}/{len(products)} products")

def main():
    scrape_product_details()

if __name__ == "__main__":
    main()
