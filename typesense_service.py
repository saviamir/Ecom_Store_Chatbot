import typesense
import hashlib
import hmac
import base64
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file

TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")
TYPESENSE_API_KEY_SEARCH = os.getenv("TYPESENSE_API_KEY_SEARCH")
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST") 
TYPESENSE_COLLECTION_NAME = "products"

# Initialize Typesense client
client = typesense.Client({
    "nodes": [{
        "host": TYPESENSE_HOST,
        "port": "443",
        "protocol": "https"
    }],
    "api_key": TYPESENSE_API_KEY,
    "search_api_key": TYPESENSE_API_KEY_SEARCH,
    "connection_timeout_seconds": 2
})


# 🔍 Search for products
def search_products(question):
    try:
        results = client.collections[TYPESENSE_COLLECTION_NAME].documents.search({
            'q': question,
            'query_by': 'name,description',  
            'per_page': 3,
            'num_typos': 2
        })

        formatted = []
        for hit in results['hits']:
            doc = hit['document']
            formatted.append(f"🛍️ {doc['name']} — Rs. {doc.get('price', 'N/A')}\n{doc.get('description', '')[:150]}...\n")

        return "\n".join(formatted) if formatted else "No matching products found."
    except Exception as e:
        return f"❌ Error searching products: {e}"



# ➕ Add a product to the collection
def add_product(product_data):
    """
    product_data = {
        "id": "1",
        "name": "Magic Vegetable Cutter",
        "description": "Chops vegetables in seconds.",
        "price": 999
    }
    """
    try:
        return client.collections[TYPESENSE_COLLECTION_NAME].documents.create(product_data)
    except Exception as e:
        return {"error": str(e)}


# 🔐 Create a scoped API key (for frontend access)
def create_scoped_key(search_only_api_key, params):
    """
    Params Example:
    {
        "filter_by": "price:>100",
        "expires_at": int(time.time()) + 3600
    }
    """
    params_str = '&'.join([f"{k}={v}" for k, v in params.items()])
    digest = hmac.new(
        search_only_api_key.encode('utf-8'),
        msg=params_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    scoped_key = base64.b64encode(digest + b':' + params_str.encode('utf-8')).decode('utf-8')
    return scoped_key


# ✅ Create collection if not exists (helper for setup)
def create_collection_if_needed():
    schema = {
        "name": TYPESENSE_COLLECTION_NAME,
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "price", "type": "int32"},
        ],
        "default_sorting_field": "price"
    }

    try:
        client.collections[TYPESENSE_COLLECTION_NAME].retrieve()
    except:
        client.collections.create(schema)


# 🧪 Example usage
if __name__ == "__main__":
    create_collection_if_needed()

    # Add a test product
    # print(add_product({
    #     "id": "1",
    #     "name": "Magic Vegetable Cutter",
    #     "description": "Chops veggies instantly!",
    #     "price": 1199
    # }))

    # Search test
    # print(search_products("vegetable"))

    # Scoped key
    # print(create_scoped_key(search_only_api_key='your_search_only_key_here', params={
    #     "filter_by": "price:>500",
    #     "expires_at": int(time.time()) + 3600
    # }))
