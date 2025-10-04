import requests
import json

all_products = []
limit = 100  # máximo permitido
skip = 0

while True:
    url = f"https://dummyjson.com/products?limit={limit}&skip={skip}"
    resp = requests.get(url)
    data = resp.json()

    products = data.get("products", [])
    all_products.extend(products)

    # se já trouxe tudo, sai do loop
    if skip + limit >= data["total"]:
        break

    skip += limit

# salva no JSON
with open("all_products.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, indent=4, ensure_ascii=False)

print(f"Total de produtos coletados: {len(all_products)}")
print("Arquivo all_products.json salvo com sucesso.")
