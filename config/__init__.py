"""Configuration loader for the Growth Operating System."""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
CONFIG_DIR = ROOT_DIR / "config"


def load_settings() -> dict:
    """Load pipeline settings from config/settings.yaml."""
    path = CONFIG_DIR / "settings.yaml"
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {}


def load_sources() -> dict:
    """Load signal source definitions from config/sources.yaml."""
    path = CONFIG_DIR / "sources.yaml"
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {}


def get_model_config(purpose: str) -> dict:
    """Get model configuration for a specific purpose.

    Args:
        purpose: One of 'strategic_inference', 'signal_interpretation',
                 'memo_generation', 'workflow_redesign', 'org_implication'

    Returns:
        Dict with 'model', 'fallback', 'temperature', 'max_tokens'
    """
    settings = load_settings()
    models = settings.get("models", {})
    if purpose in models:
        return models[purpose]
    # Default to strategic_inference config
    return models.get("strategic_inference", {
        "model": "openai/gpt-4o",
        "temperature": 0.5,
        "max_tokens": 3000,
    })


def get_db_path() -> Path:
    """Get the SQLite database path."""
    env_override = os.getenv("GROWTH_OS_DB_PATH")
    if env_override:
        return Path(env_override)
    settings = load_settings()
    rel = settings.get("memory", {}).get("db_path", "strategic_memory/growth_os.db")
    return ROOT_DIR / rel


def get_memo_output_dir() -> Path:
    """Get the directory for generated memos."""
    settings = load_settings()
    rel = settings.get("pipeline", {}).get("memo_output_dir", "operating_memos/output")
    path = ROOT_DIR / rel
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_env():
    """Load environment variables from config/.env."""
    env_path = CONFIG_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # fallback to cwd .env
