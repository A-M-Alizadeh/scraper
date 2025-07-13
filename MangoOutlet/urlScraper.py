from playwright.sync_api import sync_playwright
import time
import json
import uuid

def scroll_me():
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
        page.goto("https://www.mangooutlet.com/it/it/c/teen/teena/sconti-speciali_0f4060d7?order=asc&filters=sizes%7EXS")
        time.sleep(2)  # Wait for the page to load
        # page.click("#hf_cookie_text_cookieAccept") # Accept cookies
        
        # Wait for the cookie button to be visible and click it
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
        #scroll down to the bottom of the page
        for _ in range(10):  # Adjust the range for more or fewer scrolls
            # page.keyboard.press("End")
            # page.mouse.wheel(0,15000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            print("Scrolled down the page", _)
            time.sleep(1)
        
        # Final summary
        print(f"Scraping completed! Found {len(found_urls)} unique URLs and saved to urls.json")
        
        browser.close()


def main():
    scroll_me()

if __name__ == "__main__":
    main()