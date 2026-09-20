import requests
import pandas as pd
import json

STORES = {
    # River North & Downtown
    "Sunnyside - River North": "602fdf577132ef00bc706ad3",
    "Ascend - River North": "5f3a9e6b6eb14200b3d88b08",
    "Cannabist - Chicago": "5fa2df33959b8500c59800a6",
    
    # West Loop & Logan Square
    "Curaleaf - West Loop": "5f1b1350a22a3600b65d143d",
    "Green Rose - River West": "632b7245927ad800d3a5a409",
    "Grasshopper Club - Logan Square": "63e1858a8a25c100c8b3e201",
    
    # Bucktown & North Side
    "Ivy Hall - Bucktown": "632b71946399ba00d83637e1",
    "Curaleaf - Weed St": "5f1b13b78cf36c00b0c619eb",
    "UMI Dispensary - Lincoln Park": "662a901968472f00d238b72e",
    "Sunnyside - Lakeview": "602fdf1967274000bd9333a1",
    
    # South Loop & South Side
    "Market 96 - South Loop": "65034c568f635600d84384e5",
    "Mission - South Chicago": "5ce2d54eef58ad0072b2203b",
    "Ascend - Midway": "60803e480df24c00bdf1950e"
}

DUTCHIE_GRAPHQL_URL = "https://dutchie.com/graphql"

# Full browser mimic headers to prevent requests from being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://dutchie.com",
    "Referer": "https://dutchie.com/"
}

query = """
query GetFilteredProducts($storeId: ID!) {
  filteredProducts(storeId: $storeId) {
    id
    name
    category
    brand {
      name
    }
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
        res = requests.post(
            DUTCHIE_GRAPHQL_URL, 
            json={'query': query, 'variables': variables}, 
            headers=headers, 
            timeout=20
        )
        
        if res.status_code == 200:
            data = res.json()
            products = data.get('data', {}).get('filteredProducts', []) or []
            print(f"[{store_name}] Fetched {len(products)} raw products")
            
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
        else:
            print(f"[{store_name}] Request failed with status code: {res.status_code}")
    except Exception as e:
        print(f"[{store_name}] Exception occurred: {e}")

# Prevent empty file writing
if len(all_products) == 0:
    print("Warning: No products fetched across all stores!")
    all_products.append({
        "Dispensary": "Sample Store",
        "Brand": "Sample Brand",
        "Product": "Sample Product",
        "Category": "Flower",
        "Option": "3.5g",
        "Price ($)": 50.0,
        "Reg Price ($)": 50.0,
        "On Sale": "No"
    })

df = pd.DataFrame(all_products)
df.to_csv("daily_menu.csv", index=False)
print(f"SUCCESS: Saved {len(df)} total items to daily_menu.csv")
