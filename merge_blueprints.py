"""
Merge inteligente de blueprints:
  - Identicos: usa versao antiga
  - Mudaram + JSON valido: usa versao nova
  - Corrompidos sem mudanca: usa versao antiga
  - Corrompidos com mudanca: corrige JSON e salva versao nova
"""

import json
import os
import re
import shutil
import requests

OLD_DIR = "data/persist/blueprints"
NEW_DIR = "data_new/persist/blueprints"
OUT_DIR = "data_merged/persist/blueprints"
SERVER = "https://cardwarskingdom.pythonanywhere.com"


def safe_load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), True
    except (json.JSONDecodeError, FileNotFoundError):
        return None, False


def fix_json(raw: str) -> list | dict | None:
    """Tenta corrigir JSONs comuns do servidor."""
    text = raw

    # 1) Trailing commas antes de ] ou }
    text = re.sub(r",\s*\]", "]", text)
    text = re.sub(r",\s*\}", "}", text)

    # 2) Backslashes nao escapadas (ex: UI\Icons -> UI\\Icons)
    #    Substitui \ que nao sejam seguidas de caracteres de escape JSON validos
    text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)

    # 3) Control characters dentro de strings (newlines literais etc)
    #    Remove control chars exceto \n \r \t que ja sao validos quando escapados
    def clean_string_values(match):
        s = match.group(0)
        # Escapa control chars dentro da string
        result = []
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == '\\' and i + 1 < len(s):
                result.append(ch)
                result.append(s[i + 1])
                i += 2
                continue
            code = ord(ch)
            if code < 0x20 and ch not in ('\t',):
                if ch == '\n':
                    result.append('\\n')
                elif ch == '\r':
                    result.append('\\r')
                else:
                    result.append(' ')
            else:
                result.append(ch)
            i += 1
        return ''.join(result)

    # Aplica limpeza em strings JSON (entre aspas)
    text = re.sub(r'"(?:[^"\\]|\\.)*"', clean_string_values, text, flags=re.DOTALL)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    old_files = {f for f in os.listdir(OLD_DIR) if f.endswith(".json")}
    new_files = {f for f in os.listdir(NEW_DIR) if f.endswith(".json")}
    all_files = old_files | new_files

    stats = {"old": 0, "new": 0, "fixed": 0, "failed": 0}

    for f in sorted(all_files):
        old_path = os.path.join(OLD_DIR, f)
        new_path = os.path.join(NEW_DIR, f)
        out_path = os.path.join(OUT_DIR, f)

        old_data, old_ok = safe_load(old_path)
        new_data, new_ok = safe_load(new_path)

        # So existe no antigo
        if f not in new_files:
            shutil.copy2(old_path, out_path)
            stats["old"] += 1
            print(f"  [OLD]   {f}")
            continue

        # So existe no novo
        if f not in old_files:
            if new_ok:
                with open(out_path, "w", encoding="utf-8") as out:
                    json.dump(new_data, out, indent=2, ensure_ascii=False)
                stats["new"] += 1
                print(f"  [NEW]   {f}")
            else:
                print(f"  [FAIL]  {f}  (so existe no novo e esta corrompido)")
                stats["failed"] += 1
            continue

        # Novo OK
        if new_ok:
            if old_data == new_data:
                # Identico, usa antigo (formatacao original)
                shutil.copy2(old_path, out_path)
                stats["old"] += 1
                print(f"  [OLD]   {f}  (identico)")
            else:
                # Mudou, usa novo
                with open(out_path, "w", encoding="utf-8") as out:
                    json.dump(new_data, out, indent=2, ensure_ascii=False)
                stats["new"] += 1
                print(f"  [NEW]   {f}  (atualizado)")
            continue

        # Novo corrompido - tenta corrigir
        with open(new_path, "r", encoding="utf-8") as nf:
            raw_new = nf.read()

        # Tambem pega direto do server pra garantir
        try:
            resp = requests.get(f"{SERVER}/persist/static/Blueprints/{f}", timeout=10)
            if resp.status_code == 200:
                raw_new = resp.text
        except Exception:
            pass

        fixed = fix_json(raw_new)

        if fixed is not None:
            # Corrigiu! Checa se mudou algo
            if old_ok and fixed == old_data:
                shutil.copy2(old_path, out_path)
                stats["old"] += 1
                print(f"  [OLD]   {f}  (corrigido = identico ao antigo)")
            else:
                with open(out_path, "w", encoding="utf-8") as out:
                    json.dump(fixed, out, indent=2, ensure_ascii=False)
                stats["fixed"] += 1

                if old_ok:
                    old_count = len(old_data) if isinstance(old_data, list) else "?"
                    new_count = len(fixed) if isinstance(fixed, list) else "?"
                    print(f"  [FIXED] {f}  ({old_count} -> {new_count} entries)")
                else:
                    print(f"  [FIXED] {f}")
        else:
            # Nao conseguiu corrigir, usa antigo
            if old_ok:
                shutil.copy2(old_path, out_path)
                stats["old"] += 1
                print(f"  [OLD]   {f}  (corrompido, sem fix, manteve antigo)")
            else:
                stats["failed"] += 1
                print(f"  [FAIL]  {f}  (corrompido nos dois!)")

    # Copia manifest
    manifest_old = "data/persist/manifest.json"
    manifest_new = "data_new/persist/manifest.json"
    manifest_out = "data_merged/persist/manifest.json"
    os.makedirs(os.path.dirname(manifest_out), exist_ok=True)
    shutil.copy2(manifest_old, manifest_out)
    print(f"\n  [OLD]   manifest.json")

    print(f"\n{'='*50}")
    print(f"Resultado:")
    print(f"  Versao antiga mantida:  {stats['old']}")
    print(f"  Versao nova usada:      {stats['new']}")
    print(f"  Corrigidos com sucesso: {stats['fixed']}")
    print(f"  Falharam:               {stats['failed']}")
    print(f"\nSalvo em: {OUT_DIR}/")


if __name__ == "__main__":
    main()
