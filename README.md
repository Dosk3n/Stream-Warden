# Stream Warden

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org)

[Stream Warden](https://github.com/Dosk3n/Stream-Warden) is a Python script that intelligently manages your internet bandwidth by dynamically throttling qBittorrent upload speeds based on active streams from your media servers like Plex. **Support for Emby and Jellyfin is coming soon!** This ensures smooth streaming for you and your family or friends without your torrent uploads hogging all the bandwidth.

## Features

- **Dynamic Bandwidth Management:** Automatically reduces qBittorrent upload speeds when **Plex** media streams are active, and restores them when streams stop.
- **Multi-Media Server Support (Plex Implemented, Emby & Jellyfin Coming Soon):** Currently monitors **Plex** servers for active streams. Support for Emby and Jellyfin is planned for future releases.
- **Configurable Stream Threshold:** Define the number of concurrent streams that trigger bandwidth throttling.
- **Adjustable Poll Interval:** Set how frequently Stream Warden checks for active streams.
- **Customizable Rate Limits:** Define both default and throttled upload and download speeds for qBittorrent.
- **Detailed Logging:** Logs script activity and errors for easy monitoring and troubleshooting.
- **Simple Configuration:** Configuration is managed through an easy-to-understand `config.yml` file.

## Installation

**Before Starting:**

*   **Create a `config.yml` file:** You'll need to create a `config.yml` file locally on your system (e.g., at `/opt/stream-warden/config.yml`). You can use the example `config.yml` **available in the [GitHub repository](https://github.com/Dosk3n/Stream-Warden)** as a starting point and adjust the settings according to your preferences. **This file will be mounted into the docker container.**

### Using Docker

1.  **Pull the Docker Image**:
    ```bash
    docker pull dosk3n/stream-warden:latest
    ```

2.  **Run the Docker Container**:
    ```bash
    docker run -v /opt/stream-warden/config.yml:/stream-warden/config/config.yml -v /opt/stream-warden/logs:/stream-warden/logs dosk3n/stream-warden:latest
    ```
    This mounts your local `config.yml` and logs directories and runs Stream Warden.

### Using Docker Compose

1.  **Create a `docker-compose.yml` file**:

    ```yaml
    version: '3.8'

    services:
      stream-warden:
        image: dosk3n/stream-warden:latest
        container_name: stream-warden
        volumes:
          - /opt/stream-warden/config.yml:/stream-warden/config/config.yml
          - /opt/stream-warden/logs:/stream-warden/logs
        restart: unless-stopped
    ```

2.  **Start the Service**:
    ```bash
    docker compose up -d
    ```

3.  **Verify the container is running**:
    ```bash
    docker ps
    ```

## Configuration

All configuration for Stream Warden is done through the `config.yml` file.  **Make sure you create a copy locally as mentioned in the 'Before Starting' section.**
