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
            
            # Extract prices using specific CSS selectors for final price
            current_price = ""
            original_price = ""
            
            # Method 1: Try to find the final price using the specific class
            final_price_element = soup.find('span', class_=lambda x: x and any('SinglePrice_finalPrice' in str(cls) for cls in x))
            if final_price_element:
                current_price_text = final_price_element.get_text().strip()
                # Clean up the price text (remove extra whitespace, extract just the euro amount)
                price_match = re.search(r'€\s*(\d+[.,]\d+)', current_price_text)
                if price_match:
                    current_price = f"€{price_match.group(1)}"
            
            # Method 2: If final price not found, try regex-based approach
            if not current_price:
                final_price_element = soup.find('span', class_=re.compile(r'SinglePrice_finalPrice'))
                if final_price_element:
                    current_price_text = final_price_element.get_text().strip()
                    price_match = re.search(r'€\s*(\d+[.,]\d+)', current_price_text)
                    if price_match:
                        current_price = f"€{price_match.group(1)}"
            
            # Method 3: If final price still not found, try other price selectors but avoid crossed out prices
            if not current_price:
                # Try other common price selectors, but exclude crossed out prices
                price_selectors = [
                    'span[class*="finalPrice"]',
                    'span[class*="current"]:not([class*="crossed"])',
                    'span[class*="price"]:not([class*="crossed"])',
                    '.price-current',
                    '.final-price',
                    '.current-price'
                ]
                
                for selector in price_selectors:
                    price_elements = soup.select(selector)
                    for price_element in price_elements:
                        # Skip if this element has crossed-out styling
                        classes = ' '.join(price_element.get('class', []))
                        if 'crossed' in classes.lower():
                            continue
                            
                        price_text = price_element.get_text().strip()
                        price_match = re.search(r'€\s*(\d+[.,]\d+)', price_text)
                        if price_match:
                            current_price = f"€{price_match.group(1)}"
                            break
                    if current_price:
                        break
            
            # Try to find original price (crossed out price)
            # Look for the first (highest) crossed out price as the original price
            if not original_price:
                # Try to find original price with context first
                page_text = soup.get_text()
                original_price_match = re.search(r'Prezzo iniziale.*?€\s*(\d+[.,]\d+)', page_text, re.IGNORECASE)
                if original_price_match:
                    original_price = f"€{original_price_match.group(1)}"
            
            # If context search failed, look for crossed out elements
            if not original_price:
                crossed_price_elements = soup.find_all('span', class_=re.compile(r'SinglePrice_crossed'))
                if crossed_price_elements:
                    # Get the first crossed price (should be the original highest price)
                    for crossed_elem in crossed_price_elements:
                        orig_text = crossed_elem.get_text().strip()
                        price_match = re.search(r'€\s*(\d+[.,]\d+)', orig_text)
                        if price_match:
                            original_price = f"€{price_match.group(1)}"
                            break
            
            # If no crossed price found, try other selectors
            if not original_price:
                original_price_selectors = [
                    'span[class*="originalPrice"]',
                    'span[class*="original"]',
                    'span[class*="old"]',
                    '.price-original',
                    '.original-price',
                    '.old-price',
                    'del',
                    's'
                ]
                
                for selector in original_price_selectors:
                    orig_element = soup.select_one(selector)
                    if orig_element:
                        orig_text = orig_element.get_text().strip()
                        price_match = re.search(r'€\s*(\d+[.,]\d+)', orig_text)
                        if price_match:
                            original_price = f"€{price_match.group(1)}"
                            break
            
            # Method 4: Enhanced fallback using regex and context
            if not current_price:
                page_text = soup.get_text()
                
                # Try to find prices with their context labels
                # Look for "Prezzo attuale" (current price) context
                current_price_match = re.search(r'Prezzo attuale.*?€\s*(\d+[.,]\d+)', page_text, re.IGNORECASE)
                if current_price_match:
                    current_price = f"€{current_price_match.group(1)}"
                else:
                    # Find all Euro prices and use heuristics
                    euro_prices = re.findall(r'€\s*(\d+[.,]\d+)', page_text)
                    
                    if len(euro_prices) >= 2:
                        # Convert to float for comparison
                        prices = []
                        for price_str in euro_prices:
                            try:
                                price_val = float(price_str.replace(',', '.'))
                                formatted_price = f"€{price_str}"
                                prices.append((price_val, formatted_price))
                            except:
                                continue
                        
                        if len(prices) >= 2:
                            # Remove duplicates
                            unique_prices = []
                            seen_values = set()
                            for price_val, formatted_price in prices:
                                if price_val not in seen_values:
                                    unique_prices.append((price_val, formatted_price))
                                    seen_values.add(price_val)
                            
                            if len(unique_prices) >= 2:
                                # Sort by value - lowest should be current price (for discounted items)
                                unique_prices.sort(key=lambda x: x[0])
                                current_price = unique_prices[0][1]  # Lowest price
                                if not original_price:
                                    original_price = unique_prices[-1][1]  # Highest price
                    elif len(euro_prices) == 1:
                        current_price = f"€{euro_prices[0]}"
            
            # Extract discount percentage
            discount_amount = ""
            page_text = soup.get_text()
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
    
    for i, url in enumerate(urls, 1): #lets only get the first 10 urls
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
