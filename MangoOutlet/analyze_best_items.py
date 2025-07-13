import json
from app import parse_price, parse_discount

def analyze_best_items():
    """Analyze the best items based on different criteria"""
    
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print("🏆 BEST ITEMS ANALYSIS\n")
    print("=" * 60)
    
    # Calculate metrics for all products
    for product in products:
        product['current_price_float'] = parse_price(product.get('current_price', ''))
        product['original_price_float'] = parse_price(product.get('original_price', ''))
        product['discount_percentage'] = parse_discount(product.get('discount_amount', ''))
        
        if product['original_price_float'] > 0 and product['current_price_float'] > 0:
            product['savings_amount'] = product['original_price_float'] - product['current_price_float']
            product['savings_ratio'] = product['savings_amount'] / product['current_price_float']
            
            # Calculate value score
            discount_score = min(product['discount_percentage'] / 100, 1.0) * 40
            savings_score = min(product['savings_amount'] / 50, 1.0) * 40
            price_score = max(0, (50 - product['current_price_float']) / 50) * 20
            product['value_score'] = discount_score + savings_score + price_score
        else:
            product['savings_amount'] = 0
            product['savings_ratio'] = 0
            product['value_score'] = 0
    
    # Filter valid products
    valid_products = [p for p in products if p['current_price_float'] > 0 and p['original_price_float'] > 0]
    
    print("📊 TOP 5 BY VALUE SCORE:")
    top_value = sorted(valid_products, key=lambda x: x['value_score'], reverse=True)[:5]
    for i, product in enumerate(top_value, 1):
        print(f"{i}. {product['name'][:40]:<40} | Score: {product['value_score']:.1f} | {product['current_price']} (was {product['original_price']}) {product['discount_amount']}")
    
    print(f"\n🔥 ULTRA STEALS (80%+ off, under €8):")
    steals = [p for p in valid_products if p['discount_percentage'] >= 80 and p['current_price_float'] <= 8]
    steals.sort(key=lambda x: (-x['discount_percentage'], x['current_price_float']))
    for i, product in enumerate(steals[:5], 1):
        print(f"{i}. {product['name'][:40]:<40} | {product['current_price']} (was {product['original_price']}) {product['discount_amount']}")
    
    print(f"\n⭐ PREMIUM STEALS (€30+ → under €10):")
    premium_steals = [p for p in valid_products if p['original_price_float'] >= 30 and p['current_price_float'] <= 10]
    premium_steals.sort(key=lambda x: x['current_price_float'])
    for i, product in enumerate(premium_steals[:5], 1):
        print(f"{i}. {product['name'][:40]:<40} | {product['current_price']} (was {product['original_price']}) Save €{product['savings_amount']:.2f}")
    
    print(f"\n📊 BEST BANG FOR BUCK (Highest savings ratio):")
    best_ratio = sorted(valid_products, key=lambda x: x['savings_ratio'], reverse=True)[:5]
    for i, product in enumerate(best_ratio, 1):
        ratio = product['savings_ratio']
        print(f"{i}. {product['name'][:40]:<40} | {product['current_price']} saves €{product['savings_amount']:.2f} | Ratio: {ratio:.1f}x")
    
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"Total products analyzed: {len(valid_products)}")
    print(f"Ultra steals found: {len(steals)}")
    print(f"Premium steals found: {len(premium_steals)}")
    avg_discount = sum(p['discount_percentage'] for p in valid_products) / len(valid_products)
    avg_savings = sum(p['savings_amount'] for p in valid_products) / len(valid_products)
    print(f"Average discount: {avg_discount:.1f}%")
    print(f"Average savings: €{avg_savings:.2f}")

if __name__ == "__main__":
    analyze_best_items()
