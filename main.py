import time
import os
import re
import requests
import logging
import psutil
from plexapi.myplex import MyPlexAccount
from qbittorrentapi import Client

# --- CONFIGURATION ---
PLEX_USER = "username"
PLEX_PASS = "password"

QBIT_HOST = "127.0.0.1"
QBIT_PORT = 8080
QBIT_USER = "admin"
QBIT_PASS = "adminadmin"
QBIT_EXE_PATH = r"C:\Program Files\qBittorrent\qbittorrent.exe"

# Filtering & Alerts
MIN_SEEDERS = 5  # Minimum seeders required to even consider a torrent
# DISCORD_WEBHOOK_URL = ""  # Optional

# File Paths
HISTORY_FILE = "downloaded_history.txt"
LOG_FILE = "plex_automation.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
)


def ensure_qbit_running():
    is_running = any(proc.name().lower() == "qbittorrent.exe" for proc in psutil.process_iter(['name']))
    if not is_running:
        logging.info("Launching qBittorrent...")
        if os.path.exists(QBIT_EXE_PATH):
            os.startfile(QBIT_EXE_PATH)
            time.sleep(10)  # Time for WebUI to start
        else:
            logging.error("Could not find qBittorrent executable.")
            return False
    return True


def clean_title(title):
    title = re.sub(r'\(\d{4}\)', '', title)  # Remove year
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)  # Remove special chars
    return title.strip()


#def send_discord_notification(title, filename, category, user_name):
 #   if not DISCORD_WEBHOOK_URL: return
 #   payload = {"embeds": [{"title": f"🚀 Request by {user_name}", "color": 5763719,
 #                          "fields": [{"name": "Item", "value": title, "inline": True},
 #                                    {"name": "Type", "value": category, "inline": True}]}]}
 #   requests.post(DISCORD_WEBHOOK_URL, json=payload)


def get_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_to_history(title):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{title}\n")


def get_all_watchlists():
    items = []
    try:
        admin = MyPlexAccount(PLEX_USER, PLEX_PASS)
        # Admin watchlist
        for item in admin.watchlist():
            items.append((item.title, item.type, admin.username))
        # Home users
        for user in admin.users():
            try:
                user_ctx = admin.switchHomeUser(user.title)
                for item in user_ctx.watchlist():
                    items.append((item.title, item.type, user.title))
            except Exception:
                pass
        return items
    except Exception as e:
        logging.error(f"Plex error: {e}")
        return []


def execute_search(qbt_client, search_term):
    try:
        job = qbt_client.search_start(pattern=search_term, plugins='all', category='all')
        time.sleep(12)
        resp = qbt_client.search_results(search_id=job.id, limit=-1, offset=0)
        results = resp.get('results', [])
        job.stop()
        return results
    except Exception:
        return []


def process_search(qbt_client, search_term, category, user_name, original_title):
    results = execute_search(qbt_client, search_term)

    # FILTER: Must be a magnet link and meet MIN_SEEDERS
    valid = [r for r in results if
             r.get('fileUrl', '').startswith('magnet:') and int(r.get('nbSeeders', 0)) >= MIN_SEEDERS]

    if valid:
        # Tiebreaker: Pick highest seeder count, then largest file size (for packs)
        best = max(valid, key=lambda x: (int(x.get('nbSeeders', 0)), int(x.get('size', 0))))
        try:
            qbt_client.torrents_add(urls=best['fileUrl'], category=category)
            logging.info(f"✅ Added {category} for {user_name}: {best['fileName']}")
           # send_discord_notification(original_title, best['fileName'], category, user_name)
            return True
        except Exception:
            pass
    return False


def get_season_count(user_name, title):
    """Checks the number of seasons for a specific show."""
    try:
        admin = MyPlexAccount(PLEX_USER, PLEX_PASS)
        user_ctx = admin if user_name == PLEX_USER else admin.switchHomeUser(user_name)
        show = user_ctx.search(title, libtype='show')[0]
        return len(show.seasons())
    except:
        return 1  # Default to 1 if lookup fails


def main():
    if not ensure_qbit_running(): return
    history = get_history()
    watchlist_data = get_all_watchlists()

    try:
        qbt = Client(host=QBIT_HOST, port=QBIT_PORT, username=QBIT_USER, password=QBIT_PASS)
        qbt.auth_log_in()
    except Exception as e:
        logging.error(f"qBit login failed: {e}")
        return

    for title, p_type, u_name in watchlist_data:
        if title in history: continue

        if p_type == "movie":
            if process_search(qbt, title, "Movies", u_name, title):
                save_to_history(title)

        elif p_type == "show":
            num_seasons = get_season_count(u_name, title)
            success_count = 0
            for s in range(1, num_seasons + 1):
                s_term = f"{title} S{str(s).zfill(2)}"
                if process_search(qbt, s_term, "Shows", u_name, title):
                    success_count += 1

            if success_count > 0:
                save_to_history(title)


if __name__ == "__main__":
    main()
