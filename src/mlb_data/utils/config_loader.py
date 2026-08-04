from mlb_data.utils.paths import CONFIG_DIR
import yaml

def load_yaml(*paths: str) -> dict:
    """
    Load a YAML configuration file.

    Parameters
    ----------
    *paths : str
        Relative path from the config directory.

    Examples
    --------
    load_yaml("infrastructure", "gcp.yaml")

    load_yaml("pipelines", "schedule.yaml")

    load_yaml("models", "silver.yaml")
    """

    file_path = CONFIG_DIR.joinpath(*paths)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)