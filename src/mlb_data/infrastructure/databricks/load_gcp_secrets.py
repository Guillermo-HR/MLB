import json
import subprocess
import sys
from pathlib import Path
from mlb_data.utils import console

SCOPE = "mlb-gcp"
REQUIRED_FIELDS = [
    "project_id",
    "private_key_id",
    "private_key",
    "client_email",
    "client_id",
    "token_uri",
]

def run_databricks_secret(
    scope: str, 
    key: str, 
    value: str
) -> None:
    subprocess.run(
        [
            "databricks",
            "secrets",
            "put-secret",
            scope,
            key,
            "--string-value",
            value,
        ],
        check=True,
    )

def validate_json(
    json_path: Path
) -> None:
    
    console.print_step("Validating: ",  "JSON file")

    if not json_path.is_file():
        console.print_failed(f"File not found: {json_path}")
        sys.exit(1)

    try:
        with json_path.open("r", encoding="utf-8") as file:
            credentials = json.load(file)
    except json.JSONDecodeError as error:
        console.print_failed()
        console.print_error(f"Error parsing JSON file: {error}")
        sys.exit(1)

    missing = [
            field
            for field in REQUIRED_FIELDS
            if not credentials.get(field)
        ]
    if missing:
        console.print_failed()
        console.print_error(f"Missing required fields in JSON file: {', '.join(missing)}")
        sys.exit(1)

    console.print_success()

def get_credentials(
    json_path: Path
) -> dict:
    """
    Load and validate the GCP service account JSON file.
    """

    validate_json(json_path)

    with json_path.open("r", encoding="utf-8") as file:
        credentials = json.load(file)

    return credentials

def update_databricks_secrets(
    credentials: dict
) -> None:
    """
    Update Databricks secrets with the provided GCP service account credentials.
    """

    for field in REQUIRED_FIELDS:
        console.print_step("Updating secret", f"{field}")
        try:
            run_databricks_secret(
                SCOPE,
                field,
                credentials[field],
            )

            console.print_success()
        except Exception as e:
            console.print_failed()
            console.print_error(f"Failed to update secret {field}: {e}")

def main() -> None:
    console.print_header("Update Databricks Secrets with GCP Service Account")

    if len(sys.argv) != 2:
        console.print_error("Usage: python load_gcp_secrets.py <path_to_json>")
        sys.exit(1)

    json_path = Path(sys.argv[1])

    credentials = get_credentials(json_path)
    update_databricks_secrets(credentials)

    console.print_footer("Update Databricks Secrets with GCP Service Account")

if __name__ == "__main__":
    main()