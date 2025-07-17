from playwright.sync_api import sync_playwright
import time
import json
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def scroll_me(urls_to_scrape=None):
    """
    Scrape multiple URLs for product links
    Args:
        urls_to_scrape: List of URLs to scrape. If None, uses default URL.
    """
    if urls_to_scrape is None:
        urls_to_scrape = []
    
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
        """Recursively search for URLs starting with /it/it in JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "url" and isinstance(value, str) and value.startswith("/it/it"):
                    write_url_to_file(value)
                else:
                    extract_urls_from_json(value)
        elif isinstance(data, list):
            for item in data:
                extract_urls_from_json(item)

    def check_json(response):
        try:
            if "products" in response.url:
                print(f"Found products JSON: {response.url} - Status: {response.status}")
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
        
        # Iterate through all URLs
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


def scroll_me_concurrent(urls_to_scrape=None, max_workers=4):
    """
    Scrape multiple URLs concurrently using multiple browser tabs
    Args:
        urls_to_scrape: List of URLs to scrape. If None, uses default URL.
        max_workers: Maximum number of concurrent tabs (default: 4)
    """
    if urls_to_scrape is None:
        urls_to_scrape = []
    
    urls_file = "urls.json"
    found_urls = set()  # Keep track of URLs to avoid duplicates
    lock = threading.Lock()  # Thread-safe access to shared resources
    
    # Initialize the JSON file with an empty array
    with open(urls_file, "w", encoding='utf-8') as f:
        json.dump([], f)
    
    def write_url_to_file(url):
        """Write a single URL to the JSON file (thread-safe)"""
        with lock:  # Ensure thread-safe access
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
        """Recursively search for URLs starting with /it/it in JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "url" and isinstance(value, str) and value.startswith("/it/it"):
                    write_url_to_file(value)
                else:
                    extract_urls_from_json(value)
        elif isinstance(data, list):
            for item in data:
                extract_urls_from_json(item)

    def check_json(response):
        try:
            if "products" in response.url:
                print(f"Found products JSON: {response.url} - Status: {response.status}")
                json_data = response.json()
                # Extract URLs from this response and write to file immediately
                extract_urls_from_json(json_data)
        except Exception as e:
            print(f"Error handling response: {e}")

    def scrape_single_url(browser, url, url_index, is_first_tab=False):
        """Scrape a single URL in its own tab"""
        try:
            print(f"\n=== Starting URL {url_index + 1}/{len(urls_to_scrape)}: {url} ===")
            
            # Create new tab for this URL
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1080})
            page.on("response", lambda response: check_json(response))
            
            initial_urls_count = len(found_urls)
            
            page.goto(url)
            time.sleep(2)  # Wait for the page to load
            
            # Handle cookies only on first tab
            if is_first_tab:
                try:
                    page.wait_for_selector("#cookies\\.button\\.acceptAll", timeout=10000)
                    page.click("#cookies\\.button\\.acceptAll")  # Accept all cookies
                    print(f"Cookie banner accepted successfully for URL {url_index + 1}")
                except Exception as e:
                    print(f"Cookie button not found or not clickable for URL {url_index + 1}: {e}")
            
            # Wait for page to load with timeout
            try:
                page.wait_for_load_state("networkidle", timeout=3000)  # 3 second timeout
                print(f"Page {url_index + 1} loaded successfully (networkidle)")
            except Exception as e:
                print(f"Networkidle timeout for URL {url_index + 1}, trying alternative waiting: {e}")
                # Alternative: wait for DOM content to be loaded
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3)  # Additional wait for dynamic content
                print(f"Page {url_index + 1} loaded successfully (domcontentloaded + delay)")
            
            # Scroll down to the bottom of the page
            for scroll_count in range(25):  # Adjust the range for more or fewer scrolls
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print(f"URL {url_index + 1}: Scrolled {scroll_count + 1}/25")
                time.sleep(1)
            
            urls_found_this_page = len(found_urls) - initial_urls_count
            print(f"URL {url_index + 1} completed! Found {urls_found_this_page} new URLs")
            
            # Close the tab
            page.close()
            return url_index, urls_found_this_page
            
        except Exception as e:
            print(f"Error scraping URL {url_index + 1}: {e}")
            if 'page' in locals():
                page.close()
            return url_index, 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        # Limit concurrent tabs to avoid overwhelming the browser
        max_workers = min(max_workers, len(urls_to_scrape))
        
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_url = {
                executor.submit(scrape_single_url, browser, url, i, i == 0): (i, url) 
                for i, url in enumerate(urls_to_scrape)
            }
            
            # Process completed tasks
            completed_urls = 0
            total_urls_found = 0
            
            for future in as_completed(future_to_url):
                url_index, url = future_to_url[future]
                try:
                    _, urls_found = future.result()
                    completed_urls += 1
                    total_urls_found += urls_found
                    print(f"Progress: {completed_urls}/{len(urls_to_scrape)} URLs completed")
                except Exception as exc:
                    print(f"URL {url_index + 1} generated an exception: {exc}")
        
        # Final summary
        print(f"\n=== Concurrent scraping completed! ===")
        print(f"Total URLs scraped: {len(urls_to_scrape)}")
        print(f"Total unique product URLs found: {len(found_urls)}")
        print(f"Results saved to: {urls_file}")
        
        browser.close()


def main():
    # Example: You can now pass multiple URLs to scrape
    urls_to_scrape = [
        "https://www.mangooutlet.com/it/it/c/teen/teena/sconti-speciali_0f4060d7?order=asc&filters=sizes%7EXS",
        "https://www.mangooutlet.com/it/it/c/donna/sconti-speciali_93ea7423?filters=sizes%7EXXS_XXS-XS",
        "https://www.mangooutlet.com/it/it/c/donna/oltre-il-70_67980598?filters=sizes%7EXXS_XXS-XS",
        "https://www.mangooutlet.com/it/it/c/uomo/sconti-speciali_3b6679e9?filters=sizes%7EM"
    ]
    
    # Choose your scraping method:
    
    # Option 1: Sequential scraping (safer, slower)
    # scroll_me(urls_to_scrape)
    
    # Option 2: Concurrent scraping (faster, uses multiple tabs)
    scroll_me_concurrent(urls_to_scrape, max_workers=3)  # Adjust max_workers as needed


if __name__ == "__main__":
    main()
