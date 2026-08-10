"""
grant_permissions.py

Grant Unity Catalog privileges to Databricks Service Principals.
"""

from mlb_data.infrastructure.databricks.client import get_workspace_client
from mlb_data.infrastructure.databricks.sql_client import managed_connection
from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils import console

WORKSPACE_CLIENT = get_workspace_client()
sql_connection = managed_connection.get_connection()

def get_service_principal_application_id(
    display_name: str,
) -> str:
    """
    Get the application ID of a Service Principal by display name.

    Parameters
    ----------
    display_name : str
        Service Principal display name.

    Returns
    -------
    str
        Service Principal application ID.

    Raises
    ------
    ValueError
        If the Service Principal does not exist.
    """

    service_principals = WORKSPACE_CLIENT.service_principals.list()

    for service_principal in service_principals:
        if service_principal.display_name == display_name:
            if not service_principal.application_id:
                console.print_error(
                    f"Service Principal '{display_name}' "
                    "does not have an application ID."
                )
                raise ValueError(
                    f"Service Principal '{display_name}' "
                    "does not have an application ID."
                )

            return service_principal.application_id

    console.print_error(f"Service Principal '{display_name}' does not exist.")
    raise ValueError(
        f"Service Principal '{display_name}' does not exist."
    )

def grant_privileges(
    principal: str,
    privileges: list[str],
    securable_type: str,
    securable_name: str,
) -> None:
    """
    Grant privileges to a Service Principal.

    Parameters
    ----------
    principal : str
        Service Principal application ID.

    privileges : list[str]
        Privileges to grant.

    securable_type : str
        Type of securable object.

    securable_name : str
        Name of the securable object.
    """

    privileges_statement = ", ".join(privileges)

    statement = (
        f"GRANT {privileges_statement} "
        f"ON {securable_type} `{securable_name}` "
        f"TO `{principal}`"
    )

    with sql_connection.cursor() as cursor:
        cursor.execute(statement)

def grant_catalog_permissions(
    catalog_name: str,
    permissions: dict,
) -> None:
    """
    Grant catalog-level privileges.
    """

    for display_name, configuration in permissions.items():
        console.print_step("Granting catalog permissions",f"{display_name}: {catalog_name}")
    
        try:
            application_id = get_service_principal_application_id(display_name)
    
            grant_privileges(
                principal=application_id,
                privileges=configuration["privileges"],
                securable_type="CATALOG",
                securable_name=catalog_name,
            )

            console.print_success()
        except Exception as error:
            console.print_failed()
            console.print_error(str(error))
            raise

def grant_schema_permissions(
    schema_full_name: str,
    permissions: dict,
) -> None:
    """
    Grant schema-level privileges.
    """

    catalog_name, schema_name = schema_full_name.split(".", 1)

    securable_name = f"`{catalog_name}`.`{schema_name}`"

    for display_name, configuration in permissions.items():
        console.print_step("Granting schema permissions", f"{display_name}: {schema_full_name}")

        try:
            application_id = get_service_principal_application_id(display_name)
            privileges_statement = ", ".join(configuration["privileges"])

            statement = (
                f"GRANT {privileges_statement} "
                f"ON SCHEMA {securable_name} "
                f"TO `{application_id}`"
            )

            with sql_connection.cursor() as cursor:
                cursor.execute(statement)

            console.print_success()
        except Exception as error:
            console.print_failed()
            console.print_error(str(error))
            raise

def catalog_permissions(
    catalog_config: dict
) -> None:
    """
    Grant catalog-level privileges.
    """

    for catalog_name, permissions in catalog_config.items():
        grant_catalog_permissions(
            catalog_name=catalog_name,
            permissions=permissions,
        )

def schema_permissions(
    schema_config: dict
) -> None:
    """
    Grant schema-level privileges.
    """

    for schema_name, permissions in schema_config.items():
        grant_schema_permissions(
            schema_full_name=schema_name,
            permissions=permissions,
        )

def main() -> None:
    console.print_header("Grant Permissions")

    config = load_yaml(
        "infrastructure",
        "databricks",
        "permissions.yaml",
    )

    catalog_config = config.get("catalogs", {})
    schema_config = config.get("schemas", {})

    catalog_permissions(catalog_config)
    schema_permissions(schema_config)

    console.print_footer("Grant Permissions")

if __name__ == "__main__":
    main()