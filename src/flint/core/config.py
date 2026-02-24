import os
import sys
from pathlib import Path
from typing import Dict, Any

try:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib
except ImportError:
    tomllib = None

# Default Configuration
DEFAULT_CONFIG = {
    "backends": {"ollama_port": 11434, "lmstudio_port": 1234},
    "defaults": {"model": None},
}


def load_config() -> Dict[str, Any]:
    config_path = Path(os.path.expanduser("~/.flint/config.toml"))
    if not config_path.exists() or tomllib is None:
        return DEFAULT_CONFIG

    try:
        with open(config_path, "rb") as f:
            user_config = tomllib.load(f)

        # Merge with defaults
        config_obj = DEFAULT_CONFIG.copy()
        if "backends" in user_config:
            config_obj["backends"].update(user_config["backends"])
        if "defaults" in user_config:
            config_obj["defaults"].update(user_config["defaults"])
        return config_obj
    except Exception as e:
        print(f"Warning: Failed to parse ~/.flint/config.toml: {e}")
        return DEFAULT_CONFIG


config = load_config()
