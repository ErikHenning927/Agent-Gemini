import requests
import json

all_carts = []
limit = 100  # máximo permitido
skip = 0

while True:
    url = f"https://dummyjson.com/carts?limit={limit}&skip={skip}"
    resp = requests.get(url)
    data = resp.json()

    carts = data.get("carts", [])
    all_carts.extend(carts)

    # se já trouxe tudo, sai do loop
    if skip + limit >= data["total"]:
        break

    skip += limit

# salva no JSON
with open("all_carts.json", "w", encoding="utf-8") as f:
    json.dump(all_carts, f, indent=4, ensure_ascii=False)

print(f"Total de carrinhos coletados: {len(all_carts)}")
print("Arquivo all_carts.json salvo com sucesso.")
