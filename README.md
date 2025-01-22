# Stream Warden

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org)

Stream Warden is a Python script that intelligently manages your internet bandwidth by dynamically throttling qBittorrent upload speeds based on active streams from your media servers like Plex.  **Support for Emby and Jellyfin is coming soon!** This ensures smooth streaming for you and your family or friends without your torrent uploads hogging all the bandwidth.

## Features

*   **Dynamic Bandwidth Management:** Automatically reduces qBittorrent upload speeds when **Plex** media streams are active, and restores them when streams stop.
*   **Multi-Media Server Support (Plex Implemented, Emby & Jellyfin Coming Soon):** Currently monitors **Plex** servers for active streams. Support for Emby and Jellyfin is planned for future releases.
*   **Configurable Stream Threshold:**  Define the number of concurrent streams that trigger bandwidth throttling.
*   **Adjustable Poll Interval:** Set how frequently Stream Warden checks for active streams.
*   **Customizable Rate Limits:** Define both default and throttled upload and download speeds for qBittorrent.
*   **Detailed Logging:** Logs script activity and errors for easy monitoring and troubleshooting.
*   **Simple Configuration:**  Configuration is managed through an easy-to-understand `config.yml` file.

## Configuration

All configuration for Stream Warden is done through the `config.yml` file.
