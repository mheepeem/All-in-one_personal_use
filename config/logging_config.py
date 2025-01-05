import logging
import logging.config
import os
from pathlib import Path
from platformdirs import user_log_dir
from datetime import datetime, timedelta

# App-specific constants
APP_NAME = "AIOPU"
COMPANY_NAME = "mheepeem"
LOG_RETENTION_DAYS = 30  # Retention period in days

# Resolve the base log directory
try:
    LOG_DIR = Path(user_log_dir(APP_NAME, COMPANY_NAME))
except ImportError:
    LOG_DIR = Path.cwd() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Generate the current log file path
def get_current_log_file():
    """Generate the log file path based on the current date."""
    now = datetime.now()
    folder_name = now.strftime("%Y-%m")
    log_folder = LOG_DIR / folder_name
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file = log_folder / f"{now.strftime('%Y-%m-%d')}.log"
    return log_file

# Logging configuration
def create_logging_config():
    """Create a logging configuration dynamically."""
    log_file = get_current_log_file()
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "simple": {
                "format": "%(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": os.getenv("LOG_LEVEL", "INFO").upper(),
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "level": "DEBUG",
                "filename": str(log_file),
            },
        },
        "root": {
            "level": os.getenv("LOG_LEVEL", "DEBUG").upper(),
            "handlers": ["console", "file"],
        },
        "loggers": {
            "urllib3.connectionpool": {
                "level": "WARNING",  # Suppress debug and info messages
                "handlers": ["console", "file"],
                "propagate": False,
            }
        }
    }

# Log rotation logic
def rotate_logs():
    """Delete daily logs older than the retention period (90 days)."""
    now = datetime.now()
    cutoff_date = now - timedelta(days=LOG_RETENTION_DAYS)
    for folder in LOG_DIR.iterdir():
        if folder.is_dir():
            try:
                # Iterate over files in the folder
                for file in folder.iterdir():
                    if file.is_file() and file.suffix == ".log":
                        try:
                            file_date = datetime.strptime(file.stem, "%Y-%m-%d")
                            if file_date < cutoff_date:
                                file.unlink()  # Delete old log file
                                print(f"Deleted old log file: {file}")
                        except ValueError:
                            print(f"Skipping non-log file: {file}")
                # Remove the directory if it's empty
                if not any(folder.iterdir()):
                    folder.rmdir()
                    print(f"Deleted old log folder: {folder}")
            except ValueError:
                print(f"Skipping invalid folder name: {folder}")

class LoggingManager:
    def __init__(self, config, log_file):
        self.log_file = log_file
        self.is_first_log_today = not os.path.exists(log_file) or os.path.getsize(log_file) == 0
        logging.config.dictConfig(config)

    def write_separator(self):
        """Write the separator line with surrounding empty lines."""
        with open(self.log_file, "a") as file:
            file.write("\n")  # Empty line before the separator
            file.write("--------------------------------------------------------------------------------\n")
            file.write("\n")  # Empty line after the separator

    def log_start(self):
        """Log the start of the application."""
        logging.info("Application started.")

    def log_end(self):
        """Log the end of the application."""
        logging.info("Application ended.")
        self.write_separator()  # Add the separator with spaces

# Function to get a logger
def get_logger(name=None):
    """Retrieve a logger for a specific module."""
    return logging.getLogger(name if name else __name__)


