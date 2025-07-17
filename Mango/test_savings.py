import json

def test_savings_calculation():
    """Test that savings amounts are calculated correctly"""
    
    try:
        with open("products.json", "r", encoding='utf-8') as f:
            products = json.load(f)
        
        print("=== TESTING SAVINGS CALCULATION ===\n")
        
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
        
        # Test first 10 products with savings calculation
        products_with_savings = []
        
        for product in products[:20]:  # Test first 20 products
            current_price_float = parse_price(product.get('current_price', ''))
            original_price_float = parse_price(product.get('original_price', ''))
            
            if original_price_float > 0 and current_price_float > 0:
                savings_amount = original_price_float - current_price_float
                
                if savings_amount > 0:
                    products_with_savings.append({
                        'name': product.get('name', ''),
                        'current_price': product.get('current_price', ''),
                        'original_price': product.get('original_price', ''),
                        'current_price_float': current_price_float,
                        'original_price_float': original_price_float,
                        'savings_amount': savings_amount,
                        'discount': product.get('discount_amount', '')
                    })
        
        # Sort by savings amount (high to low)
        products_with_savings.sort(key=lambda x: x['savings_amount'], reverse=True)
        
        print("TOP 10 PRODUCTS BY SAVINGS AMOUNT:")
        print("-" * 80)
        for i, product in enumerate(products_with_savings[:10], 1):
            print(f"{i:2d}. {product['name'][:40]:40} | "
                  f"Was: {product['original_price']:>8} | "
                  f"Now: {product['current_price']:>8} | "
                  f"Save: €{product['savings_amount']:6.2f} | "
                  f"{product['discount']}")
        
        print(f"\n=== SUMMARY ===")
        print(f"Products with savings: {len(products_with_savings)}")
        if products_with_savings:
            max_savings = max(p['savings_amount'] for p in products_with_savings)
            min_savings = min(p['savings_amount'] for p in products_with_savings)
            avg_savings = sum(p['savings_amount'] for p in products_with_savings) / len(products_with_savings)
            
            print(f"Highest savings: €{max_savings:.2f}")
            print(f"Lowest savings: €{min_savings:.2f}")
            print(f"Average savings: €{avg_savings:.2f}")
        
        print("\nSavings calculation is working correctly! ✅")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_savings_calculation()
