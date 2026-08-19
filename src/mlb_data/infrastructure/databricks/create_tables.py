"""
Create Databricks Delta Lake tables.

Currently supported:
- Tables
"""

from mlb_data.infrastructure.databricks.sql_client import managed_connection
from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils import console
from mlb_data.utils.paths import DATABRICKS_CONFIG_DIR

connection = managed_connection.get_connection()

TABLES_DIR = (
    DATABRICKS_CONFIG_DIR
    / "deltalake"
    / "tables"
)


def table_exists(
    cursor,
    catalog: str,
    schema: str,
    table_name: str,
) -> bool:
    """
    Check whether a Databricks table exists.

    Parameters
    ----------
    cursor
        Databricks SQL cursor.

    catalog : str
        Databricks catalog name.

    schema : str
        Databricks schema name.

    table_name : str
        Databricks table name.

    Returns
    -------
    bool
        True if the table exists, otherwise False.
    """

    cursor.execute(
        f"""
        SHOW TABLES IN
        `{catalog}`.`{schema}`
        LIKE '{table_name}'
        """
    )

    return len(cursor.fetchall()) > 0

def validate_partition(
    table_config: dict,
    column_names: set[str],
) -> None:
    """
    Validate the optional partition configuration.
    """

    partition = table_config.get("partition")

    if not partition:
        return

    if "field" not in partition:
        console.print_failed()
        console.print_error("Partition configuration missing 'field' property.")
        raise ValueError(
            f"Table '{table_config['name']}' "
            "has a partition configuration "
            "without a field."
        )

    field = partition["field"]

    if field not in column_names:
        console.print_failed()
        console.print_error(f"Partition field '{field}' does not exist in table columns.")
        raise ValueError(
            f"Partition field '{field}' "
            f"does not exist in table "
            f"'{table_config['name']}'."
        )

def validate_table_config(
    table_config: dict,
) -> None:
    """
    Validate a Databricks table configuration.
    """

    required_fields = [
        "name",
        "schema",
        "description",
        "columns",
    ]

    for field in required_fields:
        if field not in table_config:
            console.print_failed()
            console.print_error(f"Missing required table property: {field}")
            raise ValueError(f"Missing required table property: {field}")

    if table_config["schema"] not in {"bronze", "silver"}:
        console.print_failed()
        console.print_error("invalid schema. Expected 'bronze' or 'silver'.")
        raise ValueError(
            f"Invalid schema '{table_config['schema']}'. "
            "Expected 'bronze' or 'silver'."
        )

    if not table_config["columns"]:
        console.print_failed()
        console.print_error("Table must contain at least one column.")
        raise ValueError(
            f"Table '{table_config['name']}' "
            "must contain at least one column."
        )

    column_names = set()

    for column in table_config["columns"]:
        if "name" not in column:
            console.print_failed()
            console.print_error("Column definition missing 'name' property.")
            raise ValueError(
                f"Table '{table_config['name']}' "
                "contains a column without a name."
            )

        if "type" not in column:
            console.print_failed()
            console.print_error("Column definition missing 'type' property.")
            raise ValueError(
                f"Column '{column['name']}' in table "
                f"'{table_config['name']}' "
                "does not define a type."
            )

        column_name = column["name"]
        if column_name in column_names:
            console.print_failed()
            console.print_error("Duplicate column name found in table configuration.")
            raise ValueError(
                f"Duplicate column '{column_name}' "
                f"in table '{table_config['name']}'."
            )

        column_names.add(column_name)

    validate_partition(table_config, column_names)

def build_column_definition(
    column: dict,
) -> str:
    """
    Convert a YAML column definition into
    a Databricks SQL column definition.
    """

    name = column["name"]
    data_type = column["type"].upper()
    nullable = column.get("nullable", True)
    description = column.get("description")

    definition = f"`{name}` {data_type}"

    if not nullable:
        definition += " NOT NULL"

    if description:
        definition += f" COMMENT '{description}'"

    return definition

def build_create_table_sql(
    catalog: str,
    table_config: dict,
) -> str:
    """
    Build the CREATE TABLE SQL statement.
    """

    schema = table_config["schema"]
    table_name = table_config["name"]

    columns = ",\n".join(
        f"{build_column_definition(column)}"
        for column in table_config["columns"]
    )

    statement = f"""
        CREATE TABLE IF NOT EXISTS
        `{catalog}`.`{schema}`.`{table_name}` (
        {columns}
        )
        USING DELTA
    """

    partition = table_config.get("partition")
    if partition:
        field = partition["field"]
        statement += f"PARTITIONED BY (`{field}`)\n"

    return statement

def create_table(
    cursor,
    catalog: str,
    table_config: dict,
) -> None:
    """
    Create a Databricks Delta table.
    """

    table_name = table_config["name"]
    schema = table_config["schema"]

    validate_table_config(table_config)

    console.print_step("Creating table", f"{catalog}.{schema}.{table_name}")

    if table_exists(
        cursor,
        catalog,
        schema,
        table_name,
    ):
        console.print_info("Already exists. Skipping creation.")
        return

    statement = build_create_table_sql(catalog, table_config)

    try:
        cursor.execute(
            statement
        )

        console.print_success()
    except Exception as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def create_tables(
    catalog: str,
) -> None:
    """
    Create all configured Databricks Delta tables.
    """

    for yaml_file in sorted(TABLES_DIR.glob("*.yaml")):
        table_config = load_yaml(
            "infrastructure",
            "databricks",
            "deltalake",
            "tables",
            yaml_file.name,
        )

        with managed_connection.get_connection().cursor() as cursor:
            create_table(
                cursor,
                catalog,
                table_config["table"],
            )

def main() -> None:
    """
    Create all configured Databricks Delta tables.
    """

    console.print_header("Creating Databricks Delta tables")

    catalog_config = load_yaml(
            "infrastructure",
            "databricks",
            "catalog.yaml",
        )
    catalog_name = catalog_config["catalog"]["name"]

    try:
        create_tables(catalog_name)
    except Exception as error:

        console.print_error(
            str(error)
        )

        raise

    console.print_footer("Databricks Delta tables")

if __name__ == "__main__":
    main()