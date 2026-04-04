import os
from typing import Any, Optional
from dotenv import load_dotenv

class AppConfig:
    """
    A lightweight context wrapper for the Incident Analysis Suite.
    Designed to handle configuration safely.
    """
    def __init__(self):
        # Only loads the .env once into memory
        load_dotenv()

    def fetch(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Retrieves a configuration value from the environment.
        """
        value = os.getenv(key)
        if value is None:
            return default
        return value

# Singleton instance to be used across the integration nodes
ctx = AppConfig()