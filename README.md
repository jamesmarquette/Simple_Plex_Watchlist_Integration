# Simple_Plex_Watchlist_Integration
No Warrenties or guarantees. Use at your own risk.
This python script connects to your local Plex database, retrieves the titles from your watchlist, and then uses qBittorrent's built-in search engine to find and add the best torrent (based on seeds) to your download queue.
This was designed for Windows running plex on a windows machine and qBitorrent client on windows.

A Python-based automation tool that monitors your Plex Universal Watchlist (and the watchlists of your Plex Home users) to automatically search for and download movies and TV shows via qBittorrent.
✨ Features
Multi-User Support: Scans watchlists for the Admin and all Managed Home users.
Smart TV Handling: Automatically detects the number of seasons for a show and searches for full Season Packs.
Automatic Organization: Assigns qBittorrent categories (Movies or Shows) to ensure files are saved to the correct folders.
Process Management: Automatically launches qBittorrent on Windows if it isn't running.
Failure Protection: Includes a retry mechanism that cleans titles (removes years/special chars) if a primary search fails.
Health Filtering: Only adds magnet links with a minimum seeder count to ensure fast downloads.
Notifications: Sends beautiful Discord embeds whenever a new download starts.
History Tracking: Maintains a local database to prevent duplicate downloads.
🛠️ Prerequisites
Python 3.8+
qBittorrent with Web UI enabled:
Go to Tools > Options > Web UI.
Enable "Web User Interface".
Set the port (default: 8080).
Search Plugins: Ensure qBittorrent has search plugins installed and updated (Search tab > Search plugins > Check for updates).

📥 Installation
Clone the repository:
bash
git clone https://github.com
cd Simple_Plex_Watchlist_Integration

Install dependencies:
bash
pip install plexapi qbittorrent-api psutil requests

