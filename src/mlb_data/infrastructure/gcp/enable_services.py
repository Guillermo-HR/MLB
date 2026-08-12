"""
enable_services.py

Enable the Google Cloud services required by the project.
"""

from mlb_data.utils.config_loader import load_yaml
from mlb_data.infrastructure.gcp.gcloud import GCloudError, run_gcloud
from mlb_data.utils import console

def service_enabled(
    project_id: str,
    service: str
) -> bool:
    """
    Check whether a Google Cloud service is enabled.

    Parameters
    ----------
    project_id : str
        Google Cloud project ID.

    service : str
        Google Cloud service name.

    Returns
    -------
    bool
        True if the service is enabled, otherwise False.
    """

    try:
        result = run_gcloud(
            "services",
            "list",
            "--enabled",
            f"--filter=config.name:{service}",
            "--format=value(config.name)",
            project=project_id
        )

        return result.stdout.strip() == service
    except Exception:
        return False

def enable_service(
    project_id: str,
    service: str
) -> None:
    """
    Enable a Google Cloud service.
    """

    console.print_step("Enabling", service)

    if service_enabled(project_id, service):
        console.print_info("Already enabled. Skipping.")
        return

    try:
        run_gcloud(
            "services",
            "enable",
            service,
            project=project_id,
        )

        console.print_success()
    except GCloudError as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def main() -> None:
    console.print_header("Enable Google Cloud services")
    
    gcp_config = load_yaml(
        "infrastructure",
        "gcp",
        "gcp.yaml"
    )

    project_id = gcp_config["project"]["project_id"]
    services = gcp_config["services"]

    for service in services:
        enable_service(
            project_id,
            service
        )

    console.print_footer("Enable Google Cloud services")

if __name__ == "__main__":
    main()