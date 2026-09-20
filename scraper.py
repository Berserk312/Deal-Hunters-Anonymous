import requests
import pandas as pd
import json

STORES = {
    "Sunnyside - River North": "602fdf577132ef00bc706ad3",
    "Ivy Hall - Bucktown": "632b71946399ba00d83637e1",
    "Cannabist - Chicago": "5fa2df33959b8500c59800a6",
    "Curaleaf - West Loop": "5f1b1350a22a3600b65d143d"
}

DUTCHIE_GRAPHQL_URL = "https://dutchie.com/graphql"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json"
}

query = """
query GetFilteredProducts($storeId: ID!) {
  filteredProducts(storeId: $storeId) {
    name
    category
    brand { name }
    variants {
      option
      priceRec
      specialPriceRec
    }
  }
}
"""

all_products = []

for store_name, store_id in STORES.items():
    variables = {"storeId": store_id}
    try:
        res = requests.post(DUTCHIE_GRAPHQL_URL, json={'query': query, 'variables': variables}, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            products = data.get('data', {}).get('filteredProducts', []) or []
            
            for p in products:
                brand_obj = p.get('brand')
                brand = brand_obj.get('name') if isinstance(brand_obj, dict) else 'Unknown Brand'
                category = p.get('category', 'Other')
                
                variants = p.get('variants', []) or []
                for v in variants:
                    reg_price = v.get('priceRec', 0) or 0
                    special_price = v.get('specialPriceRec')
                    effective_price = special_price if special_price is not None else reg_price
                    
                    all_products.append({
                        "Dispensary": store_name,
                        "Brand": brand,
                        "Product": p.get('name', 'Unknown'),
                        "Category": category,
                        "Option": v.get('option', 'N/A'),
                        "Price ($)": float(effective_price),
                        "Reg Price ($)": float(reg_price),
                        "On Sale": "Yes" if special_price is not None else "No"
                    })
    except Exception as e:
        print(f"Skipping {store_name} due to error: {e}")

# Always create daily_menu.csv even if empty so git commit doesn't fail
if not all_products:
    all_products = [{
        "Dispensary": "None", "Brand": "None", "Product": "None", 
        "Category": "None", "Option": "None", "Price ($)": 0.0, 
        "Reg Price ($)": 0.0, "On Sale": "No"
    }]

df = pd.DataFrame(all_products)
df.to_csv("daily_menu.csv", index=False)
print(f"Successfully wrote {len(df)} records to daily_menu.csv")

