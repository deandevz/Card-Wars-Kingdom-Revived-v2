# Card Wars Kingdom — Revived Server

A reverse-engineered private server for **Card Wars Kingdom** (v1.0.17 / v1.19.1), forked from [shishkabob27/CardWarsKingdom](https://github.com/shishkabob27/CardWarsKingdom) and fixed to actually work.

> **Disclaimer**: This server is intended for personal and educational use only. It lacks production-grade security — only run it locally or with people you trust.

---

## What was fixed

The original repository had several issues that prevented the game from connecting properly. This fork includes the following fixes:

- Switched `server_settings.json` URLs from `https` to `http` (required for local servers without SSL)
- Added missing route `/persist/static/Blueprints/<filename>` for serving blueprint data
- Added missing route `/persist/<player_id>/game` for game state persistence
- Added missing route `/persist/friends_informationDW/` for friends system
- Auto-generation of `messages_received_ids.json` (no more manual file creation)
- Moved `db.create_all()` before `app.run()` to ensure the database is initialized on first launch
- Disabled the level anti-cheat check in `update_deck_name` (was blocking legitimate gameplay)

Now you can run it without Wi-Fi :D

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/deandevz/Card-Wars-Kingdom-Revived.git
cd Card-Wars-Kingdom-Revived
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the game client

Inside your **game folder** (not the server folder), navigate to:

```
Card Wars Kingdom_data/StreamingAssets/server_settings.json
```

Change both `server_url` and `local_server_url` to point to your local server:

```json
{
  "server_url": "http://127.0.0.1:5000",
  "local_server_url": "http://127.0.0.1:5000"
}
```

> Make sure to use `http`, not `https`.

---

## Running the Server

### Quick start (recommended)

After setting up the venv once, you can use the provided script to auto-activate the environment and start the server:

```bash
chmod +x run-app.sh
./run-app.sh
```

### Manual start

```bash
source venv/bin/activate
python app.py
```

By default the server runs on port **5000**. To use a different port:

```bash
python app.py --port 8080
```

### Using Gunicorn (optional)

```bash
pip install gunicorn
gunicorn app:app --bind 127.0.0.1:5000
```

---

## Updating Blueprints (Game Data)

All game content (creatures, spells, factions, shop items, etc.) is defined by the JSON blueprint files in `data/persist/blueprints/`. The upstream server at `https://cardwarskingdom.pythonanywhere.com` may have newer content (e.g., new factions like Magmalands).

Two scripts are included to pull and merge updated data:

### Project structure

```
data/persist/blueprints/       # Active blueprints used by your server
data_new/persist/blueprints/   # Downloaded from the upstream server (raw)
data_merged/persist/blueprints/ # Merged result (ready to use)
```

### Step 1 — Download latest blueprints

```bash
python3 download_blueprints.py
```

This downloads all blueprint JSONs from the upstream server into `data_new/persist/blueprints/`.

### Step 2 — Merge with your local data

```bash
python3 merge_blueprints.py
```

This compares your current `data/persist/blueprints/` with `data_new/persist/blueprints/` and produces a clean merged version in `data_merged/persist/blueprints/`. The merge logic:

- **Identical files** → keeps your local version
- **Changed files with valid JSON** → uses the updated version
- **Corrupted files with no changes** → keeps your local version
- **Corrupted files with new content** → auto-fixes the JSON and uses the corrected version

### Step 3 — Apply the merged data

Replace your active blueprints with the merged result:

```bash
rm -rf data/persist/blueprints
cp -r data_merged/persist/blueprints data/persist/blueprints
```

Restart the server and the new content will be available.

> **Note**: The database (`cardwarskingdom.db`) does not need to change — it only stores player data. All game content comes from the blueprint JSONs.

---

## Additional Setup

For PVP and chat functionality, set up Chat and PUN servers with [Photon](https://www.photonengine.com/) and update `photon_chat_app_id` and `photon_pun_app_id` in `server_settings.json`.

---

## Credits

- Original server by [shishkabob27](https://github.com/shishkabob27)
- Upstream server and game client by [CardWarsRevived](https://github.com/Sgsysysgsgsg/Card-Wars-Kingdom-Revived)
- Fixes and improvements by [deandevz](https://github.com/deandevz)
- Special thanks to **Seven7z** for making me bang my head against the wall until I figured out all the bugs
