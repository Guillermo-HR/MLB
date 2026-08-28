"""
create_service_principals.py

Create the Databricks Service Principals required by the project.
"""

from databricks.sdk.errors import NotFound
from mlb_data.infrastructure.databricks.client import get_workspace_client
from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils import console


WORKSPACE_CLIENT = get_workspace_client()

def service_principal_exists(
    display_name: str,
) -> bool:
    """
    Check whether a Service Principal exists by display name.

    Parameters
    ----------
    display_name : str
        Service Principal display name.

    Returns
    -------
    bool
        True if the Service Principal exists, otherwise False.
    """

    service_principals = WORKSPACE_CLIENT.service_principals.list()

    return any(
        service_principal.display_name == display_name
        for service_principal in service_principals
    )

def create_service_principal(
    service_principal: dict,
) -> None:
    """
    Create a Service Principal if it does not already exist.

    Parameters
    ----------
    service_principal : dict
        Service Principal configuration.
    """

    display_name = service_principal["display_name"]

    console.print_step("Creating service principal", display_name)

    if service_principal_exists(display_name):
        console.print_info("Already exists. Skipping creation.")
        return

    try:
        WORKSPACE_CLIENT.service_principals.create(
            display_name=display_name,
        )

        console.print_success()
    except Exception as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def main() -> None:
    console.print_header("Create Service Principals")

    config = load_yaml(
        "infrastructure",
        "databricks",
        "service_principals.yaml",
    )

    service_principals = config["service_principals"]

    for service_principal in service_principals.values():
        create_service_principal(service_principal)

    console.print_footer("Create Service Principals")

if __name__ == "__main__":
    main()