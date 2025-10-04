import requests
import json
import os

def fetch_all(url_base, key_in_response=None, limit=100):
    all_items = []
    skip = 0

    while True:
        url = f"{url_base}?limit={limit}&skip={skip}"
        resp = requests.get(url)
        data = resp.json()

        items = data[key_in_response] if key_in_response else data
        all_items.extend(items)

        total = data.get("total", len(items))
        if skip + limit >= total:
            break
        skip += limit

    return all_items

# --- Pasta de destino ---
folder = "json"
os.makedirs(folder, exist_ok=True)  # cria a pasta se não existir

# --- Recursos ---
resources = {
    "products": {"url": "https://dummyjson.com/products", "key": "products"},
    "carts": {"url": "https://dummyjson.com/carts", "key": "carts"},
    "users": {"url": "https://dummyjson.com/users", "key": "users"},
    "posts": {"url": "https://dummyjson.com/posts", "key": "posts"},
    "comments": {"url": "https://dummyjson.com/comments", "key": "comments"},
    "todos": {"url": "https://dummyjson.com/todos", "key": "todos"},
    "quotes": {"url": "https://dummyjson.com/quotes", "key": "quotes"},
}

for name, info in resources.items():
    print(f"Coletando {name}...")
    data = fetch_all(info["url"], key_in_response=info["key"])
    filename = os.path.join(folder, f"{name}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"{len(data)} registros de {name} salvos em {filename}")

print("Todos os recursos foram coletados e salvos dentro da pasta 'json'!")
