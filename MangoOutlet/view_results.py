#!/usr/bin/env python3
"""
Quick Results Viewer - Creates web interface from existing scraped data
"""

import json
import time
import webbrowser
import http.server
import socketserver
import threading
from datetime import datetime

def create_html_results():
    """Create an HTML file to display the scraping results"""
    
    # Load the scraped data
    try:
        with open('products_beautifulsoup.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        products = []
    
    try:
        with open('urls.json', 'r', encoding='utf-8') as f:
            urls = json.load(f)
        total_urls = len(urls)
    except FileNotFoundError:
        total_urls = 0
    
    # Calculate statistics
    total_products = len(products)
    successful_scrapes = sum(1 for p in products if p.get('name'))
    
    # Create HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mango Outlet Scraping Results</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2d3436;
        }}
        
        .stat-label {{
            color: #636e72;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .product-card {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .product-card:hover {{
            transform: translateY(-5px);
        }}
        
        .product-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f1f2f6;
        }}
        
        .product-info {{
            padding: 20px;
        }}
        
        .product-name {{
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2d3436;
        }}
        
        .price-info {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .current-price {{
            font-size: 1.2em;
            font-weight: bold;
            color: #00b894;
        }}
        
        .original-price {{
            text-decoration: line-through;
            color: #636e72;
        }}
        
        .discount {{
            background: #e17055;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .no-image {{
            width: 100%;
            height: 200px;
            background: #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-style: italic;
        }}
        
        .timestamp {{
            text-align: center;
            padding: 20px;
            color: #636e72;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
        }}
        
        .success-badge {{
            color: #00b894;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛍️ Mango Outlet Scraping Results</h1>
            <p>Complete scraping results using <strong>BeautifulSoup</strong> - No browser needed!</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_urls}</div>
                <div class="stat-label">Total URLs Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_products}</div>
                <div class="stat-label">Products Scraped</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #00b894;">{successful_scrapes}</div>
                <div class="stat-label">Successful Extractions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #e17055;">{(successful_scrapes/total_products*100) if total_products > 0 else 0:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>
        
        <div class="products-grid">
"""

    # Add product cards
    for i, product in enumerate(products):
        name = product.get('name', 'Unknown Product')
        current_price = product.get('current_price', '')
        original_price = product.get('original_price', '')
        discount = product.get('discount_amount', '')
        image_url = product.get('image_url', '')
        
        # Create image HTML
        if image_url:
            image_html = f'<img src="{image_url}" alt="{name}" class="product-image" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\'">'
            no_image_html = '<div class="no-image" style="display:none;">No image available</div>'
        else:
            image_html = ''
            no_image_html = '<div class="no-image">No image available</div>'
        
        # Create price HTML
        price_html = ''
        if current_price:
            price_html += f'<span class="current-price">{current_price}</span>'
        if original_price and original_price != current_price:
            price_html += f'<span class="original-price">{original_price}</span>'
        if discount:
            price_html += f'<span class="discount">{discount}</span>'
        
        html_content += f"""
            <div class="product-card">
                {image_html}
                {no_image_html}
                <div class="product-info">
                    <div class="product-name">{name}</div>
                    <div class="price-info">
                        {price_html}
                    </div>
                </div>
            </div>
        """

    # Close HTML
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content += f"""
        </div>
        
        <div class="timestamp">
            <p>Generated on {current_time}</p>
            <p class="success-badge">✅ BeautifulSoup scraping successful - {successful_scrapes} products extracted!</p>
            <p>🚀 Much faster than Playwright/Selenium - No browser automation needed!</p>
        </div>
    </div>
</body>
</html>
"""

    # Save HTML file
    with open('results.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML results created: results.html")
    return 'results.html'

def start_web_server():
    """Start a simple web server to serve the HTML file"""
    PORT = 8000
    
    # Find an available port
    for port in range(8000, 8010):
        try:
            with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
                PORT = port
                break
        except OSError:
            continue
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    def serve():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌐 Web server started at http://localhost:{PORT}")
            print(f"📱 Opening results in your browser...")
            httpd.serve_forever()
    
    # Start server in background thread
    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()
    
    # Open browser
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}/results.html')
    
    return PORT

def main():
    """Main function to create web interface from existing data"""
    print("🎯 Mango Outlet Results Viewer")
    print("=" * 50)
    
    # Create HTML results
    print("🎨 Creating Web Interface...")
    html_file = create_html_results()
    
    # Start web server and open browser
    print("🌐 Starting Web Server...")
    port = start_web_server()
    
    print(f"\n{'='*50}")
    print("🎉 RESULTS READY!")
    print(f"{'='*50}")
    print(f"🌐 View results at: http://localhost:{port}/results.html")
    print(f"📁 HTML file: results.html")
    print(f"\n💡 Press Ctrl+C to stop the web server")
    
    try:
        # Keep the server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n👋 Web server stopped. Thanks for viewing the results!")

if __name__ == "__main__":
    main()
