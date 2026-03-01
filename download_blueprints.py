import json
import os
import requests

SERVER_URL = "https://cardwarskingdom.pythonanywhere.com"
OUTPUT_DIR = "data_new/persist/blueprints"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Baixando blueprints do servidor online...")
    resp = requests.get(f"{SERVER_URL}/persist/static/blueprints")
    resp.raise_for_status()
    blueprints = resp.json()

    print(f"Total de arquivos: {len(blueprints)}")

    for item in blueprints:
        name = item["name"]
        raw = item["data"]
        path = os.path.join(OUTPUT_DIR, f"{name}.json")

        # Tenta parsear como JSON, se falhar salva o raw direto
        try:
            data = json.loads(raw)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            with open(path, "w", encoding="utf-8") as f:
                f.write(raw)
            print(f"  !!  {name}.json (JSON invalido, salvo raw)")
            continue

        print(f"  OK  {name}.json")

    # Baixar manifest
    print("Baixando manifest.json...")
    resp = requests.get(f"{SERVER_URL}/persist/static/manifest.json")
    resp.raise_for_status()
    manifest_path = os.path.join("data_new/persist", "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("  OK  manifest.json")

    print(f"\nPronto! {len(blueprints)} arquivos salvos em {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
