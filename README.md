# Simple_Plex_Watchlist_Integration
No Warrenties or guarantees. Use at your own risk.
No support will be provided.  Feel free to let me know if you find better ways to do this.  
This is for testing and learning purposes only.
It is wise to always use a VPN on you system that is running qBittorrent. 

This is a much simpler method of automating your Plex requests and downloads (probably less secure as well).  It is a bit buggy, sometimes it will download incorrect shows or movies.  It tries to download full shows with all it's seasons but sometimes it only downloads the 1st season or which ever has the most "seeds" in torrents. 

This python script connects to your local Plex database, retrieves the titles from your users watchlist, and then uses qBittorrent's built-in search engine to find and add the best torrent (based on seeds) to your download queue.
This was designed for Windows running plex on a windows machine and qBitorrent client on windows.
Feel free to alter. 
A Python-based automation tool that monitors your Plex Universal Watchlist (and the watchlists of your Plex Home users) to automatically search for and download movies and TV shows via qBittorrent.

✨ Features
Multi-User Support: Scans watchlists for the Admin and all Managed Home users.
Token Authentication: Uses X-Plex-Token for secure, rate-limit-free access to your account.
High-Accuracy Matching: Uses Regex and Fuzzy logic to ensure correct torrent selection (e.g., skips "Gabby's Dollhouse" for "Dollhouse").
Smart TV Handling: Detects season counts and searches for full Season Packs.
Automatic Organization: Assigns categories (Movies/Shows) for automatic folder orting.
Process Management: Launches qBittorrent automatically if it isn't running. 

🛠️ Prerequisites
Python 3.8+
qBittorrent with Web UI enabled (Tools > Options > Web UI).
Search Plugins: Must be updated in qBittorrent (Search tab > Search plugins > Check for updates).

⚙️ Configuration
1. Finding your Plex Token
To avoid rate-limiting errors, this script requires an X-Plex-Token .
Sign in to Plex Web App in your browser  .
Navigate to any movie or episode in your library.
Click the three dots (...) and select Get Info .
Click View XML at the bottom left .
In the new tab that opens, look at the URL in your address bar. Your token is the string after X-Plex-Token= at the very end . 
2. Update main.py
Paste your token and update the connection details:
python
PLEX_TOKEN = "PASTE_YOUR_TOKEN_HERE"
QBIT_HOST = "127.0.0.1"
QBIT_PORT = 8080
QBIT_EXE_PATH = r"C:\Program Files\qBittorrent\qbittorrent.exe"


🛠️ Prerequisites
Python 3.x installed.
qBittorrent Web API: Ensure it is enabled in your qBittorrent settings under Tools > Options > Web UI.
Python Libraries: Install the required qBittorrent API wrapper.
In Terminal:
pip install qbittorrent-api
pip install plexapi qbittorrent-api
 
Accessing the Local Plex Database
The Plex database is typically located in your Application Support or Local AppData folder. You can query the metadata_items table to find items where watchlist_id is set. 

Common Database Locations:
Windows: %LOCALAPPDATA%\Plex Media Server\Plug-in Support\Databases\com.plexapp.plugins.library.db

qBittorrent with Web UI enabled:
Go to Tools > Options > Web UI.
Enable "Web User Interface".
Set the port (default: 8080).
Search Plugins: Ensure qBittorrent has search plugins installed and updated (Search tab > Search plugins > Check for updates).

# this may need to be altered if running on a different machine
QBIT_HOST = "127.0.0.1"
QBIT_PORT = 8080
QBIT_USER = "admin"
QBIT_PASS = "adminadmin"

# Update this to your qBittorrent install path
QBIT_EXE_PATH = r"C:\Program Files\qBittorrent\qbittorrent.exe"

# Optional qBittorrent configuration:
Create catagories in qBittorrent
Edit catagories to download to a different folder - perhaps the folders where plex is watching such as Shows, Movies, Music. 

📥 Installation
bash
# Clone and install dependencies
git clone https://github.com
cd plex-qbit-automator
pip install plexapi qbittorrent-api psutil requests
Use code with caution.
🚀 Usage
Run the script manually or set it as a scheduled task:

python main.py
Use code with caution.
📂 Automatic Sorting
In qBittorrent, create these categories to enable auto-moving:
Movies: Set path to your Movie library folder.
Shows: Set path to your TV library folder.
Ensure "Automatic Torrent Management" is enabled in qBit settings.
⚠️ Important Notes
Security: Never share your X-Plex-Token publicly; it provides full access to your account.
History: The script creates downloaded_history.txt to avoid duplicate downloads.
Magnets Only: Only magnet: links are accepted to prevent bencoded string errors. 

It should look into the plex db find all of your users, check watchlists and search in qBittorrent to download items
