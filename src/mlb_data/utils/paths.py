from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONFIG_DIR = PROJECT_ROOT / "config"

INFRASTRUCTURE_CONFIG_DIR = CONFIG_DIR / "infrastructure"

GCP_CONFIG_DIR = INFRASTRUCTURE_CONFIG_DIR / "gcp"

DATABRICKS_CONFIG_DIR = INFRASTRUCTURE_CONFIG_DIR / "databricks"