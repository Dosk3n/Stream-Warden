import yaml
import logging
import logging.handlers
import time
from plexapi.server import PlexServer
import qbittorrentapi

# --- Configuration Loading ---
CONFIG_FILE = "config.yml"

def load_config():
    """Loads configuration from config.yml."""
    try:
        with open(CONFIG_FILE, "r", encoding='utf-8') as f: # Explicitly specify UTF-8 encoding
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Error: {CONFIG_FILE} not found. Please make sure it exists in the same directory as the script.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing {CONFIG_FILE}: {e}")
        exit(1)

config = load_config()

# --- Logging Setup ---
LOG_LEVEL_STR = config['stream_warden']['log_level'].upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO) # Default to INFO if invalid level

LOG_FILE = "stream_warden.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB (Maximum log file size before rotation)
LOG_BACKUP_COUNT = 5            # Keep 5 backup log files

# Get root logger
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

# Formatter for logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler (logs to screen)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Rotating file handler (logs to file with size limit and rotation)
rotating_file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT
)
rotating_file_handler.setFormatter(formatter)
logger.addHandler(rotating_file_handler)

logging.info("Stream Warden script started.")

# --- Plex Stream Checking ---
def get_plex_stream_count(plex_config):
    """Gets the current number of active Plex streams."""
    if not plex_config['enabled']:
        logging.debug("Plex monitoring is disabled in config.")
        return 0

    plex_url = plex_config['url']
    plex_token = plex_config['token']

    try:
        plex_server = PlexServer(plex_url, plex_token)
        sessions = plex_server.sessions()
        stream_count = len(sessions)
        logging.debug(f"Plex streams: {stream_count}")
        return stream_count
    except Exception as e:
        logging.error(f"Error connecting to Plex: {e}")
        return 0

# --- qBittorrent API Interaction ---
def get_qbittorrent_client(qbittorrent_config):
    """Creates and authenticates a qBittorrent API client."""
    conn_info = dict(
        host=qbittorrent_config['url'],
        username=qbittorrent_config['username'],
        password=qbittorrent_config['password'],
    )

    try:
        qbt_client = qbittorrentapi.Client(**conn_info)
        qbt_client.auth_log_in()  # Explicit login for older qbittorrent versions.
        qbt_client.auth_log_out()

        return qbt_client
    except qbittorrentapi.LoginFailed as e:
        logging.error(f"qBittorrent Login failed: {e}")
        return None
    except Exception as e:
        logging.error(f"Error connecting to qBittorrent: {e}")
        return None

def set_qbittorrent_alternative_mode(qbt_client, enabled):
    """Enables or disables qBittorrent alternative speed limits mode."""
    if qbt_client is None:
        logging.warning("qBittorrent client not initialized, cannot set alternative mode.")
        return

    try:
        qbt_client.transfer.set_speed_limits_mode(intended_state=enabled)
        mode_status = "enabled" if enabled else "disabled"
        logging.info(f"qBittorrent alternative mode {mode_status}.")
    except Exception as e:
        logging.error(f"Error setting qBittorrent alternative mode: {e}")


def set_qbittorrent_rate_limits(qbt_client, upload_limit_kibs, download_limit_kibs):
    """Sets qBittorrent GLOBAL rate limits to the provided upload and download values (in KiB/s)."""
    if qbt_client is None:
        logging.warning("qBittorrent client not initialized, cannot set rate limits.")
        return

    try:
        upload_limit_bytes = upload_limit_kibs * 1024 # Convert KiB/s to bytes/s
        download_limit_bytes = download_limit_kibs * 1024 # Convert KiB/s to bytes/s
        logging.info(f"Setting qBittorrent GLOBAL rate limits - Upload: {upload_limit_kibs:.2f} KiB/s, Download: {download_limit_kibs:.2f} KiB/s")

        qbt_client.transfer.set_upload_limit(limit=upload_limit_bytes)
        qbt_client.transfer.set_download_limit(limit=download_limit_bytes)

    except Exception as e:
        logging.error(f"Error setting qBittorrent rate limits: {e}")


if __name__ == "__main__":
    qbt_client = get_qbittorrent_client(config['qbittorrent']) # Initialize qbt_client once at startup

    if qbt_client: # Proceed only if qbt_client is successfully initialized
        set_qbittorrent_alternative_mode(qbt_client, False) # Disable alternative mode as we only use global speed limits
        set_qbittorrent_rate_limits(qbt_client, config['qbittorrent']['rate_limits']['default']['upload'], config['qbittorrent']['rate_limits']['default']['download']) # Set default rate limits
        current_rate_limit_state = "default" # Initialize state
        previous_stream_count = -1

        while True:
            total_stream_count = 0

            # --- Plex Stream Check ---
            plex_stream_count = get_plex_stream_count(config['plex'])
            total_stream_count += plex_stream_count

            if total_stream_count != previous_stream_count:
                logging.info(f"Total stream count: {total_stream_count}")
                previous_stream_count = total_stream_count # Update previous count only when it changes
            else:
                logging.debug(f"Stream count unchanged ({total_stream_count}), skipping log.")

            stream_threshold = config['stream_warden']['stream_threshold']

            if total_stream_count >= stream_threshold:
                desired_rate_limit_state = "throttled"
            else:
                desired_rate_limit_state = "default"

            if desired_rate_limit_state != current_rate_limit_state:
                if desired_rate_limit_state == "throttled":
                    set_qbittorrent_rate_limits(qbt_client, config['qbittorrent']['rate_limits']['throttled']['upload'], config['qbittorrent']['rate_limits']['throttled']['download'])
                else: # desired_rate_limit_state == "default"
                    set_qbittorrent_rate_limits(qbt_client, config['qbittorrent']['rate_limits']['default']['upload'], config['qbittorrent']['rate_limits']['default']['download'])
                current_rate_limit_state = desired_rate_limit_state
                logging.info(f"Rate limit state changed to: {current_rate_limit_state}")
            else:
                logging.debug(f"Rate limit state unchanged ({current_rate_limit_state}), skipping rate limit update.")


            time.sleep(config['stream_warden']['poll_interval'])
    else:
        logging.error("qBittorrent client initialization failed. Script exiting.")
        exit(1)