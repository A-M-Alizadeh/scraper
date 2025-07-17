from playwright.sync_api import sync_playwright
import time
import json
import uuid

def scroll_me(urls_to_scrape=None):
    """
    Scrape multiple URLs for product links
    Args:
        urls_to_scrape: List of URLs to scrape. If None, uses default URLs.
    """
    if urls_to_scrape is None:
        urls_to_scrape = [
            "https://shop.mango.com/it/it/c/donna/saldi--50_93ea7423?filters=sizes%7EXXS",
            "https://shop.mango.com/it/it/c/uomo/saldi--50_3b6679e9?filters=sizes%7EM",
            "https://shop.mango.com/it/it/c/teen/teena/saldi--50_0f4060d7?filters=sizes%7EXS"
        ]
    
    urls_file = "urls.json"
    found_urls = set()  # Keep track of URLs to avoid duplicates
    
    # Initialize the JSON file with an empty array
    with open(urls_file, "w", encoding='utf-8') as f:
        json.dump([], f)
    
    def write_url_to_file(url):
        """Write a single URL to the JSON file"""
        if url not in found_urls:
            found_urls.add(url)
            # Read existing URLs
            try:
                with open(urls_file, "r", encoding='utf-8') as f:
                    urls = json.load(f)
            except:
                urls = []
            
            # Add new URL and write back
            urls.append(url)
            with open(urls_file, "w", encoding='utf-8') as f:
                json.dump(urls, f, indent=4, ensure_ascii=False)
            print(f"Added URL to file: {url}")
    
    def extract_urls_from_json(data):
        """Recursively search for URLs containing /p/ in JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "url" and isinstance(value, str) and "/p/" in value:
                    # Ensure it's a full URL
                    if value.startswith("/"):
                        full_url = f"https://shop.mango.com{value}"
                    else:
                        full_url = value
                    write_url_to_file(full_url)
                else:
                    extract_urls_from_json(value)
        elif isinstance(data, list):
            for item in data:
                extract_urls_from_json(item)

    def check_json(response):
        try:
            if "shop.mango.com" in response.url and "json" in response.headers.get("content-type", "").lower():
                print(f"Found JSON response: {response.url} - Status: {response.status}")
                json_data = response.json()
                # Extract URLs from this response and write to file immediately
                extract_urls_from_json(json_data)
        except Exception as e:
            print(f"Error handling response: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 1080})
        page.on("response", lambda response: check_json(response))
        
        # Iterate through all URLs sequentially
        for i, url in enumerate(urls_to_scrape, 1):
            print(f"\n=== Scraping URL {i}/{len(urls_to_scrape)}: {url} ===")
            
            page.goto(url)
            time.sleep(2)  # Wait for the page to load
            
            # Handle cookies only on first page
            if i == 1:
                try:
                    page.wait_for_selector("#cookies\\.button\\.acceptAll", timeout=10000)
                    page.click("#cookies\\.button\\.acceptAll")  # Accept all cookies
                    print("Cookie banner accepted successfully")
                except Exception as e:
                    print(f"Cookie button not found or not clickable: {e}")
            
            # Wait for page to load with timeout
            try:
                page.wait_for_load_state("networkidle", timeout=3000)  # 3 second timeout
                print("Page loaded successfully (networkidle)")
            except Exception as e:
                print(f"Networkidle timeout, trying alternative waiting: {e}")
                # Alternative: wait for DOM content to be loaded
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3)  # Additional wait for dynamic content
                print("Page loaded successfully (domcontentloaded + delay)")
            
            # Scroll down to the bottom of the page
            initial_urls_count = len(found_urls)
            for scroll_count in range(25):  # Adjust the range for more or fewer scrolls
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print(f"Scrolled down the page {scroll_count + 1}/25")
                time.sleep(1)
            
            urls_found_this_page = len(found_urls) - initial_urls_count
            print(f"Found {urls_found_this_page} new URLs from this page")
        
        # Final summary
        print(f"\n=== Scraping completed! ===")
        print(f"Total URLs scraped: {len(urls_to_scrape)}")
        print(f"Total unique product URLs found: {len(found_urls)}")
        print(f"Results saved to: {urls_file}")
        
        browser.close()


def main():
    # URLs to scrape - add more URLs to this list as needed
    urls_to_scrape = [
        "https://shop.mango.com/it/it/c/donna/saldi--50_93ea7423?filters=sizes%7EXXS",
        "https://shop.mango.com/it/it/c/uomo/saldi--50_3b6679e9?filters=sizes%7EM",
        "https://shop.mango.com/it/it/c/teen/teena/saldi--50_0f4060d7?filters=sizes%7EXS"
    ]
    
    # Scrape all URLs and save to one JSON file
    scroll_me(urls_to_scrape)

if __name__ == "__main__":
    main()
