import time
import os
import re
import requests
import logging
import psutil
from difflib import SequenceMatcher
from plexapi.myplex import MyPlexAccount
from qbittorrentapi import Client

# --- CONFIGURATION ---
PLEX_TOKEN = "InsertTokenFromPlexWebXML"

QBIT_HOST = "127.0.0.1"
QBIT_PORT = 8080
QBIT_USER = "admin"
QBIT_PASS = "adminadmin"
QBIT_EXE_PATH = r"C:\Program Files\qBittorrent\qbittorrent.exe"

# Filtering & Alerts
MIN_SEEDERS = 5
MATCH_THRESHOLD = 0.8  # 80% similarity (raise to 0.9 if still getting wrong items)
DISCORD_WEBHOOK_URL = ""

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
            time.sleep(10)
        else:
            logging.error("Could not find qBittorrent executable.")
            return False
    return True


def normalize_text(text):
    """Lowercase and remove everything except letters, numbers, and spaces."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return ' '.join(text.split())


def is_strict_match(target_title, torrent_name):
    """Regex word boundary and fuzzy similarity check."""
    clean_target = normalize_text(target_title)
    clean_torrent = normalize_text(torrent_name)

    # Word Boundary Check: Prevents 'Gabby's Dollhouse' matching 'Dollhouse'
    pattern = rf"\b{re.escape(clean_target)}\b"
    if not re.search(pattern, clean_torrent):
        return False

    # Fuzzy Similarity: Checks if the target represents the bulk of the filename
    # We compare the target to the start of the torrent name
    score = SequenceMatcher(None, clean_target, clean_torrent[:len(clean_target) + 5]).ratio()
    return score >= MATCH_THRESHOLD


def get_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_to_history(title):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{title}\n")


def send_discord_notification(title, filename, category, user_name):
    if not DISCORD_WEBHOOK_URL: return
    payload = {"embeds": [{"title": f"🚀 Request by {user_name}", "color": 5763719,
                           "fields": [{"name": "Item", "value": title, "inline": True},
                                      {"name": "Type", "value": category, "inline": True}]}]}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except:
        pass


def get_all_watchlists():
    items = []
    try:
        admin = MyPlexAccount(token=PLEX_TOKEN)
        for item in admin.watchlist():
            items.append((item.title, item.type, admin.username))
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

    # Filter for magnets and seeders
    valid = [r for r in results if
             r.get('fileUrl', '').startswith('magnet:') and int(r.get('nbSeeders', 0)) >= MIN_SEEDERS]

    filtered_results = []
    for r in valid:
        if is_strict_match(original_title, r.get('fileName', '')):
            filtered_results.append(r)
        else:
            logging.debug(f"Blocked mismatch: '{r.get('fileName')}'")

    if filtered_results:
        best = max(filtered_results, key=lambda x: (int(x.get('nbSeeders', 0)), int(x.get('size', 0))))
        try:
            qbt_client.torrents_add(urls=best['fileUrl'], category=category)
            logging.info(f"✅ Added {category} for {user_name}: {best['fileName']}")
            send_discord_notification(original_title, best['fileName'], category, user_name)
            return True
        except Exception:
            pass
    return False


def get_season_count(user_name, title):
    try:
        admin = MyPlexAccount(PLEX_USER, PLEX_PASS)
        user_ctx = admin if user_name == PLEX_USER else admin.switchHomeUser(user_name)
        show = user_ctx.search(title, libtype='show')
        return len(show[0].seasons()) if show else 1
    except:
        return 1


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
