import typesense
import csv
import os
from dotenv import load_dotenv
load_dotenv()

client = typesense.Client({
    "nodes": [{
        "host": os.getenv("TYPESENSE_HOST"),
        "port": os.getenv("TYPESENSE_PORT", 443),
        "protocol": os.getenv("TYPESENSE_PROTOCOL")
    }],
    "api_key": os.getenv("TYPESENSE_API_KEY"),
    "search_api_key": os.getenv("TYPESENSE_API_KEY_SEARCH"),
    "connection_timeout_seconds": 2
})

# Define Typesense schema
schema = {
    "name": "products",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "description", "type": "string"},
        {"name": "price", "type": "float"},
        {"name": "category", "type": "string", "facet": True},
        {"name": "vendor", "type": "string", "facet": True},
        {"name": "tags", "type": "string[]", "facet": True}
    ],
    "default_sorting_field": "price"
}

# Recreate collection
try:
    client.collections['products'].delete()
except:
    pass

client.collections.create(schema)

# Upload data from Shopify CSV
with open('products_export_1.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    id_counter = 1
    for row in reader:
        try:
            product = {
                "handle": row.get("Handle", f"product-{id_counter}"),
                "id": row.get("Handle") or str(id_counter),
                "name": row.get("Title", ""),
                "description": row.get("Body (HTML)", ""),
                "price": float(row.get("Variant Price", 0.0) or 0.0),
                "category": row.get("Type", "General"),
                "vendor": row.get("Vendor", "Unknown"),
                "tags": [tag.strip() for tag in row.get("Tags", "").split(",") if tag.strip()]
            }

            client.collections['products'].documents.upsert(product)
            id_counter += 1

        except Exception as e:
            print(f"Error on row {id_counter}: {e}")

print("✅ Products uploaded to Typesense successfully.")
