"""
create_catalog.py

Create the Databricks Unity Catalog required by the project.
"""

from mlb_data.infrastructure.databricks.sql_client import managed_connection
from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils import console

sql_connection = managed_connection.get_connection()

def schema_exists(
    catalog_name: str,
    schema_name: str
) -> bool:
    """
    Check whether a schema exists.

    Parameters
    ----------
    connection
        Active Databricks SQL connection.

    catalog_name : str
        Catalog name.

    schema_name : str
        Schema name.

    Returns
    -------
    bool
        True if the schema exists, otherwise False.
    """

    with sql_connection.cursor() as cursor:
        cursor.execute(
            f"SHOW SCHEMAS IN `{catalog_name}`"
        )

        schemas = cursor.fetchall()

    return any(
        schema[0] == schema_name
        for schema in schemas
    )

def create_schema(
    catalog_name: str,
    schema: dict,
) -> None:
    """
    Create a schema if it does not already exist.

    Parameters
    ----------
    connection
        Active Databricks SQL connection.

    catalog_name : str
        Catalog containing the schema.

    schema : dict
        Schema configuration.
    """

    name = schema["name"]
    comment = schema.get("comment")

    console.print_step("Creating schema", f"{catalog_name}.{name}")

    if schema_exists(catalog_name, name):
        console.print_info("Already exists. Skipping creation.")
        return

    sql_statement = f"CREATE SCHEMA IF NOT EXISTS `{catalog_name}`.`{name}`"

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

def create_schemas(
    schema_config: dict
) -> None:
    """
    Create schemas in a Databricks catalog.
    """
    
    catalog_name = schema_config["catalog"]
    schemas = schema_config.get("schemas", [])

    for schema in schemas:
        create_schema(catalog_name, schema)

def main() -> None:
    console.print_header("Create Schemas")

    schema_config = load_yaml(
        "infrastructure",
        "databricks",
        "schemas.yaml",
    )

    create_schemas(schema_config)

    console.print_footer("Create Schemas")

if __name__ == "__main__":
    main()