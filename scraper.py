import pandas as pd
import json
import time
from curl_cffi import requests

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

all_products = []

session = requests.Session(impersonate="chrome120")

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://dutchie.com",
    "referer": "https://dutchie.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for store_name, store_id in STORES.items():
    url = f"https://dutchie.com/api/v2/embedded-menu/{store_id}/products"
    
    try:
        res = session.get(url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            products = res.json()
            if isinstance(products, list):
                print(f"[{store_name}] Successfully fetched {len(products)} products")
                
                for p in products:
                    brand = p.get('brandName') or (p.get('brand', {}).get('name') if isinstance(p.get('brand'), dict) else 'Unknown Brand')
                    category = p.get('category', 'Other')
                    
                    variants = p.get('variants', []) or []
                    if not variants:
                        reg_price = p.get('priceRec', 0) or p.get('unitPrice', 0) or 0
                        special_price = p.get('specialPriceRec') or p.get('specialPrice')
                        effective_price = special_price if special_price is not None else reg_price
                        
                        all_products.append({
                            "Dispensary": store_name,
                            "Brand": brand,
                            "Product": p.get('name', 'Unknown'),
                            "Category": category,
                            "Option": "Standard",
                            "Price ($)": float(effective_price),
                            "Reg Price ($)": float(reg_price),
                            "On Sale": "Yes" if special_price is not None else "No"
                        })
                    else:
                        for v in variants:
                            reg_price = v.get('priceRec', 0) or v.get('price', 0) or 0
                            special_price = v.get('specialPriceRec') or v.get('specialPrice')
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
            print(f"[{store_name}] Status Code: {res.status_code}")
            
    except Exception as e:
        print(f"[{store_name}] Exception: {e}")
        
    time.sleep(1)

# Completely removed the hardcoded mock array!
if len(all_products) > 0:
    df = pd.DataFrame(all_products)
    df.to_csv("daily_menu.csv", index=False)
    print(f"SUCCESS: Saved {len(df)} total live products to daily_menu.csv!")
else:
    print("WARNING: Zero items fetched. Cloudflare blocked endpoint.")
