import pandas as pd
import json
import time
from playwright.sync_api import sync_playwright

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

with sync_playwright() as p:
    # Launch real headless Chromium browser
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for store_name, store_id in STORES.items():
        url = f"https://dutchie.com/embedded-menu/{store_id}"
        print(f"[{store_name}] Loading page...")

        try:
            # Go directly to the embedded menu page to pass Cloudflare checks
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            # Execute GraphQL fetch inside the authenticated browser context
            graphql_query = """
            async (storeId) => {
                const res = await fetch('https://dutchie.com/graphql', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: `query GetFilteredProducts($storeId: ID!) {
                            filteredProducts(storeId: $storeId) {
                                name
                                category
                                brand { name }
                                variants { option priceRec specialPriceRec }
                            }
                        }`,
                        variables: { storeId: storeId }
                    })
                });
                return await res.json();
            }
            """

            result = page.evaluate(graphql_query, store_id)
            products = result.get('data', {}).get('filteredProducts', []) or []
            print(f"[{store_name}] Successfully fetched {len(products)} live products")

            for item in products:
                brand = item.get('brand', {}).get('name', 'Unknown Brand') if isinstance(item.get('brand'), dict) else 'Unknown Brand'
                category = item.get('category', 'Other')

                for v in item.get('variants', []) or []:
                    reg_price = v.get('priceRec', 0) or 0
                    special_price = v.get('specialPriceRec')
                    effective_price = special_price if special_price is not None else reg_price

                    all_products.append({
                        "Dispensary": store_name,
                        "Brand": brand,
                        "Product": item.get('name', 'Unknown'),
                        "Category": category,
                        "Option": v.get('option', 'N/A'),
                        "Price ($)": float(effective_price),
                        "Reg Price ($)": float(reg_price),
                        "On Sale": "Yes" if special_price is not None else "No"
                    })

        except Exception as e:
            print(f"[{store_name}] Failed: {e}")

    browser.close()

if len(all_products) > 0:
    df = pd.DataFrame(all_products)
    df.to_csv("daily_menu.csv", index=False)
    print(f"SUCCESS: Wrote {len(df)} real live products to daily_menu.csv!")
else:
    print("ERROR: No products pulled.")
