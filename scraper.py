import requests
import pandas as pd
import json

STORES = {
    # River North & Downtown
    "Sunnyside - River North": "602fdf577132ef00bc706ad3",
    "Ascend - River North": "5f3a9e6b6eb14200b3d88b08",
    "Cannabist - Chicago": "5fa2df33959b8500c59800a6",
    
    # West Loop, Fulton Market & Near West Side
    "Curaleaf - West Loop": "5f1b1350a22a3600b65d143d",
    "Green Rose - River West": "632b7245927ad800d3a5a409",
    "Grasshopper Club - Logan Square": "63e1858a8a25c100c8b3e201",
    
    # Bucktown, Wicker Park & Logan Square
    "Ivy Hall - Bucktown": "632b71946399ba00d83637e1",
    "Ascend - Logan Square": "5f3a9ed404c00000a6a7c88b",
    "Maribis - Westchester/Chicago": "5d2f6236b3ba19008f1b6a12",
    
    # Lincoln Park, Lakeview & North Side
    "Curaleaf - Weed St": "5f1b13b78cf36c00b0c619eb",
    "UMI Dispensary - Lincoln Park": "662a901968472f00d238b72e",
    "Sunnyside - Lakeview": "602fdf1967274000bd9333a1",
    "Ivy Hall - Glendale Heights/North": "632b71cb6399ba00d83637e4",
    
    # South Loop, Pilsen & South Side
    "Market 96 - South Loop": "65034c568f635600d84384e5",
    "Mission - South Chicago": "5ce2d54eef58ad0072b2203b",
    "Ivy Hall - Peoria/Chicago": "632b71e16399ba00d83637e7",
    "Ascend - Midway": "60803e480df24c00bdf1950e"
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

if not all_products:
    all_products = [{
        "Dispensary": "None", "Brand": "None", "Product": "None", 
        "Category": "None", "Option": "None", "Price ($)": 0.0, 
        "Reg Price ($)": 0.0, "On Sale": "No"
    }]

df = pd.DataFrame(all_products)
df.to_csv("daily_menu.csv", index=False)
print(f"Successfully written {len(df)} records across all Chicago dispensaries to daily_menu.csv")
