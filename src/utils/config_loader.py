"""Configuration loader utility."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration settings."""

    def __init__(self, config_path: str = None):
        """Initialize configuration loader.

        Args:
            config_path: Path to config file. If None, uses default.
        """
        # Load environment variables from .env file (if it exists)
        # This allows local testing with .env file while GitHub Actions uses secrets
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Configuration dictionary.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Dot-separated key path (e.g., 'blog.output_dir')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_env(self, key: str, default: str = None) -> str:
        """Get environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value
        """
        return os.getenv(key, default)
