import requests
import typesense
import os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE = os.getenv("wcfpdr-rh.myshopify.com")  # wcfpdr-rh.myshopify.com
SHOPIFY_ACCESS_TOKEN = os.getenv("e989de1ebe3e52f64418d48b59ccccb6")

TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST")
TYPESENSE_COLLECTION_NAME = "products"

# Initialize Typesense
client = typesense.Client({
    "nodes": [{
        "host": TYPESENSE_HOST,
        "port": "443",
        "protocol": "https"
    }],
    "api_key": TYPESENSE_API_KEY,
    "connection_timeout_seconds": 2
})

def fetch_shopify_products():
    url = f"https://{SHOPIFY_STORE}/admin/api/2023-10/products.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return data["products"]

def sync_to_typesense(products):
    for product in products:
        product_data = {
            "id": str(product["id"]),
            "name": product["title"],
            "description": product["body_html"],
            "price": int(float(product["variants"][0]["price"]))
        }

        try:
            client.collections[TYPESENSE_COLLECTION_NAME].documents.upsert(product_data)
            print(f"✔ Synced: {product['title']}")
        except Exception as e:
            print(f"❌ Error syncing {product['title']}: {e}")

if __name__ == "__main__":
    products = fetch_shopify_products()
    sync_to_typesense(products)
