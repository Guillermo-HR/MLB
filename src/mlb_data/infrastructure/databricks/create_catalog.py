"""
create_catalog.py

Create the Databricks Unity Catalog required by the project.
"""

from mlb_data.infrastructure.databricks.sql_client import managed_connection
from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils import console

sql_connection = managed_connection.get_connection()

def catalog_exists(
    name: str
) -> bool:
    """
    Check whether a catalog exists.

    Parameters
    ----------
    connection
        Active Databricks SQL connection.

    name : str
        Catalog name.

    Returns
    -------
    bool
        True if the catalog exists, otherwise False.
    """

    with sql_connection.cursor() as cursor:
        cursor.execute("SHOW CATALOGS")
        catalogs = cursor.fetchall()

    return any(
        catalog[0] == name
        for catalog in catalogs
    )

def create_catalog(
    catalog: dict
) -> None:
    """
    Create a Databricks catalog if it does not already exist.

    Parameters
    ----------
    connection
        Active Databricks SQL connection.

    catalog : dict
        Catalog configuration.
    """

    name = catalog["name"]
    comment = catalog.get("comment")

    console.print_step("Creating catalog", name)

    if catalog_exists(name):
        console.print_info("Already exists. Skipping creation.")
        return

    sql_statement = f"CREATE CATALOG IF NOT EXISTS `{name}`"

    if comment:
        escaped_comment = comment.replace(
            "'",
            "''",
        )
        sql_statement += f" COMMENT '{escaped_comment}'"

    try:
        with sql_connection.cursor() as cursor:
            cursor.execute(sql_statement)

        console.print_success()
    except Exception as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def main() -> None:
    console.print_header("Create Catalog")

    catalog_config = load_yaml(
        "infrastructure",
        "databricks",
        "catalog.yaml",
    )

    create_catalog(catalog_config["catalog"])

    console.print_footer("Create Catalog")

if __name__ == "__main__":
    main()