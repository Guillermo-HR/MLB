"""
create_service_accounts.py

Create the Google Cloud service accounts required by the project.
"""

from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils.gcloud import GCloudError, run_gcloud
from mlb_data.utils import console

def service_account_exists(
    project_id: str,
    account_id: str
) -> bool:
    """
    Check whether a service account exists.

    Parameters
    ----------
    project_id : str
        Google Cloud project ID.

    account_id : str
        Service account ID.

    Returns
    -------
    bool
        True if the service account exists, otherwise False.
    """

    email = f"{account_id}@{project_id}.iam.gserviceaccount.com"

    try:
        run_gcloud(
            "iam",
            "service-accounts",
            "describe",
            email,
            project=project_id,
        )

        return True
    except GCloudError:
        return False

def create_service_account(
    project_id: str,
    service_account: dict
) -> None:
    """
    Create a Google Cloud service account.
    """

    account_id = service_account["id"]
    display_name = service_account["display_name"]
    description = service_account.get("description", "")

    console.print_step("Creating service account", account_id)

    if service_account_exists(project_id, account_id):
        console.print_info("Already exists. Skipping creation.")
        return

    try:
        run_gcloud(
            "iam",
            "service-accounts",
            "create",
            account_id,
            f"--display-name={display_name}",
            f"--description={description}",
            project=project_id,
        )

        console.print_success()
    except GCloudError as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def main() -> None:
    console.print_header("Create Service Accounts")

    gcp_config = load_yaml(
        "infrastructure",
        "gcp",
        "gcp.yaml"
    )
    service_accounts_config = load_yaml(
        "infrastructure",
        "gcp",
        "service_accounts.yaml"
    )

    project_id = gcp_config["project"]["project_id"]

    for service_account in service_accounts_config["service_accounts"].values():
        create_service_account(
            project_id,
            service_account
        )

    console.print_footer("Create Service Accounts")

if __name__ == "__main__":
    main()