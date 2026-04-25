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
Smart TV Handling: Automatically detects the number of seasons for a show and searches for full Season Packs.
Automatic Organization: Assigns qBittorrent categories (Movies or Shows) to ensure files are saved to the correct folders.
Process Management: Automatically launches qBittorrent on Windows if it isn't running.
Failure Protection: Includes a retry mechanism that cleans titles (removes years/special chars) if a primary search fails.
Health Filtering: Only adds magnet links with a minimum seeder count to ensure fast downloads.
Notifications: Sends beautiful Discord embeds whenever a new download starts.
History Tracking: Maintains a local database to prevent duplicate downloads.

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

Configuration
Open main.py and update the CONFIGURATION section:
python
PLEX_USER = "YourPlexUsername"
PLEX_PASS = "YourPlexPassword"

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


Installation:
Download main.py
Alter the main.py lines 11 and 12 with your own credentials
Run Python script. 
I should look into the plex db find all of your users, check watchlists and search in qBittorrent to download items
