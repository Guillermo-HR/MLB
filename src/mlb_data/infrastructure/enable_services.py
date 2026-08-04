from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils.gcloud import run_gcloud

def enable_service(project_id: str, service: str) -> None:
    print(f"Service: {service}")

    run_gcloud(
        "services",
        "enable",
        service,
        project=project_id,
    )

    print(f"Service {service} enabled successfully.\n")

def main() -> None:
    config = load_yaml("infrastructure", "gcp.yaml")

    project_id = config["project"]["project_id"]
    services = config["services"]

    for service in services:
        enable_service(project_id, service)

    print("\nServices enabled successfully.")

if __name__ == "__main__":
    main()