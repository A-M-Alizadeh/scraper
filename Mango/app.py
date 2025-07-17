from flask import Flask, render_template, jsonify, request
import json
import re
from typing import List, Dict

app = Flask(__name__)

def parse_price(price_str: str) -> float:
    """Convert price string like '€22,99' to float 22.99"""
    if not price_str or price_str == 'N/A':
        return 0.0
    # Remove € symbol and replace comma with dot
    price_clean = price_str.replace('€', '').replace(',', '.')
    try:
        return float(price_clean)
    except:
        return 0.0

def parse_discount(discount_str: str) -> int:
    """Convert discount string like '-85%' to integer 85"""
    if not discount_str or discount_str == 'N/A':
        return 0
    # Extract number from string like '-85%'
    match = re.search(r'-?(\d+)%', discount_str)
    if match:
        return int(match.group(1))
    return 0

def load_and_sort_products(sort_by='discount_desc') -> List[Dict]:
    """Load products and sort them based on the specified criteria"""
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # Add calculated values for advanced filtering
        for product in products:
            product['current_price_float'] = parse_price(product.get('current_price', ''))
            product['original_price_float'] = parse_price(product.get('original_price', ''))
            product['discount_percentage'] = parse_discount(product.get('discount_amount', ''))
            
            # Calculate savings amount
            if product['original_price_float'] > 0 and product['current_price_float'] > 0:
                product['savings_amount'] = product['original_price_float'] - product['current_price_float']
                # Calculate savings ratio (savings per euro spent)
                product['savings_ratio'] = product['savings_amount'] / product['current_price_float'] if product['current_price_float'] > 0 else 0
                # Calculate "value score" - composite score for best deals
                discount_score = min(product['discount_percentage'] / 100, 1.0) * 40  # Max 40 points
                savings_score = min(product['savings_amount'] / 50, 1.0) * 40  # Max 40 points (€50+ savings = full points)
                price_score = max(0, (50 - product['current_price_float']) / 50) * 20  # Max 20 points (under €0 = full points)
                product['value_score'] = discount_score + savings_score + price_score
            else:
                product['savings_amount'] = 0
                product['savings_ratio'] = 0
                product['value_score'] = 0
        
        # Apply sorting based on sort_by parameter
        if sort_by == 'price_asc':
            products.sort(key=lambda x: x['current_price_float'])
        elif sort_by == 'price_desc':
            products.sort(key=lambda x: x['current_price_float'], reverse=True)
        elif sort_by == 'discount_desc':
            products.sort(key=lambda x: x['discount_percentage'], reverse=True)
        elif sort_by == 'discount_asc':
            products.sort(key=lambda x: x['discount_percentage'])
        elif sort_by == 'savings_desc':
            products.sort(key=lambda x: x['savings_amount'], reverse=True)
        elif sort_by == 'savings_asc':
            products.sort(key=lambda x: x['savings_amount'])
        elif sort_by == 'value_score':
            products.sort(key=lambda x: x['value_score'], reverse=True)
        elif sort_by == 'savings_ratio':
            products.sort(key=lambda x: x['savings_ratio'], reverse=True)
        elif sort_by == 'steals':  # Ultra deals: 80%+ discount AND under €8
            products = [p for p in products if p['discount_percentage'] >= 80 and p['current_price_float'] <= 8]
            products.sort(key=lambda x: (-x['discount_percentage'], x['current_price_float']))
        elif sort_by == 'premium_steals':  # €30+ original price, now under €10
            products = [p for p in products if p['original_price_float'] >= 30 and p['current_price_float'] <= 10]
            products.sort(key=lambda x: x['current_price_float'])
        elif sort_by == 'name_asc':
            products.sort(key=lambda x: x.get('name', '').lower())
        elif sort_by == 'name_desc':
            products.sort(key=lambda x: x.get('name', '').lower(), reverse=True)
        else:
            # Default: Sort by discount percentage (high to low), then by current price (low to high)
            products.sort(key=lambda x: (-x['discount_percentage'], x['current_price_float']))
        
        return products
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

@app.route('/')
def index():
    """Main page showing all products"""
    sort_by = request.args.get('sort', 'default')
    products = load_and_sort_products(sort_by)
    return render_template('index.html', products=products, 
                         min_discount=0, max_price=None, min_price=0, min_savings=0, sort_by=sort_by)

@app.route('/api/products')
def api_products():
    """API endpoint to get products data"""
    products = load_and_sort_products()
    return jsonify(products)

@app.route('/filter')
def filter_products():
    """Filter and sort products by various criteria"""
    # Get sort parameter
    sort_by = request.args.get('sort', 'default')
    products = load_and_sort_products(sort_by)
    
    # Get filter parameters
    min_discount = request.args.get('min_discount', type=int, default=0)
    max_price = request.args.get('max_price', type=float, default=None)
    min_price = request.args.get('min_price', type=float, default=0)
    min_savings = request.args.get('min_savings', type=float, default=0)
    
    # Apply filters
    filtered_products = []
    for product in products:
        price_check = True
        if max_price is not None:
            price_check = min_price <= product['current_price_float'] <= max_price
        else:
            price_check = product['current_price_float'] >= min_price
            
        savings_check = product['savings_amount'] >= min_savings
            
        if (product['discount_percentage'] >= min_discount and price_check and savings_check):
            filtered_products.append(product)
    
    return render_template('index.html', products=filtered_products, 
                         min_discount=min_discount, max_price=max_price, min_price=min_price, 
                         min_savings=min_savings, sort_by=sort_by)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
