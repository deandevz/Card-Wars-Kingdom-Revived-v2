import json
import os

OLD_DIR = "data/persist/blueprints"
NEW_DIR = "data_new/persist/blueprints"

def safe_load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), True
    except (json.JSONDecodeError, FileNotFoundError):
        return None, False

def count_entries(data):
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        return len(data)
    return 0

def get_factions(data):
    if not isinstance(data, list):
        return set()
    return {item["Faction"] for item in data if isinstance(item, dict) and "Faction" in item}

def get_ids(data):
    if not isinstance(data, list):
        return set()
    return {item["ID"] for item in data if isinstance(item, dict) and "ID" in item}

def main():
    old_files = {f for f in os.listdir(OLD_DIR) if f.endswith(".json")}
    new_files = {f for f in os.listdir(NEW_DIR) if f.endswith(".json")}

    only_old = old_files - new_files
    only_new = new_files - old_files
    common = old_files & new_files

    changed = []
    identical = []
    new_broken = []

    for f in sorted(common):
        old_data, old_ok = safe_load(os.path.join(OLD_DIR, f))
        new_data, new_ok = safe_load(os.path.join(NEW_DIR, f))

        if not new_ok:
            new_broken.append(f)
            continue

        if not old_ok:
            changed.append((f, "old broken", None))
            continue

        if old_data == new_data:
            identical.append(f)
        else:
            old_count = count_entries(old_data)
            new_count = count_entries(new_data)

            old_ids = get_ids(old_data)
            new_ids = get_ids(new_data)
            added_ids = new_ids - old_ids
            removed_ids = old_ids - new_ids

            old_factions = get_factions(old_data)
            new_factions = get_factions(new_data)
            new_factions_added = new_factions - old_factions

            info = {
                "entries": f"{old_count} -> {new_count}" if old_count != new_count else str(old_count),
                "added_ids": len(added_ids),
                "removed_ids": len(removed_ids),
                "new_factions": new_factions_added if new_factions_added else None,
                "sample_added": sorted(added_ids)[:10] if added_ids else None,
            }
            changed.append((f, "changed", info))

    # Print report
    print("=" * 70)
    print("DIFF: data/persist/blueprints vs data_new/persist/blueprints")
    print("=" * 70)

    print(f"\n--- IDENTICOS (nao precisam trocar): {len(identical)} ---")
    for f in sorted(identical):
        print(f"  {f}")

    print(f"\n--- MUDARAM (precisam trocar): {len(changed)} ---")
    for f, reason, info in changed:
        if info:
            print(f"\n  {f}")
            print(f"    Entries: {info['entries']}")
            if info["added_ids"]:
                print(f"    IDs adicionados: +{info['added_ids']}")
            if info["removed_ids"]:
                print(f"    IDs removidos: -{info['removed_ids']}")
            if info["new_factions"]:
                print(f"    Factions novas: {info['new_factions']}")
            if info["sample_added"]:
                print(f"    Exemplos novos: {info['sample_added']}")
        else:
            print(f"\n  {f} ({reason})")

    print(f"\n--- CORROMPIDOS no data_new (usar versao antiga): {len(new_broken)} ---")
    for f in sorted(new_broken):
        old_data, old_ok = safe_load(os.path.join(OLD_DIR, f))
        status = "OK no antigo" if old_ok else "BROKEN nos dois!"
        print(f"  {f}  ({status})")

    if only_new:
        print(f"\n--- SO EXISTEM no data_new: {len(only_new)} ---")
        for f in sorted(only_new):
            print(f"  {f}")

    if only_old:
        print(f"\n--- SO EXISTEM no antigo: {len(only_old)} ---")
        for f in sorted(only_old):
            print(f"  {f}")

if __name__ == "__main__":
    main()
