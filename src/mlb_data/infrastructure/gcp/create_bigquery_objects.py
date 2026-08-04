"""
create_bigquery_objects.py

Create BigQuery objects.

Currently supported:
- Tables
"""

from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils import console
from mlb_data.utils.paths import GCP_CONFIG_DIR

TABLES_DIR = (
    GCP_CONFIG_DIR
    / "bigquery"
    / "tables"
)

def load_schema(
    schema: list[dict]
) -> list[bigquery.SchemaField]:
    """
    Convert a YAML schema definition into BigQuery SchemaField objects.
    """

    return [
        bigquery.SchemaField(
            name=field["name"],
            field_type=field["type"],
            mode=field.get("mode", "NULLABLE"),
            description=field.get("description")
        )
        for field in schema
    ]

def table_exists(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    table_id: str
) -> bool:
    """
    Check whether a BigQuery table exists.

    Parameters
    ----------
    client : bigquery.Client
        BigQuery client.

    project_id : str
        Google Cloud project ID.

    dataset_id : str
        BigQuery dataset ID.

    table_id : str
        BigQuery table ID.

    Returns
    -------
    bool
        True if the table exists, otherwise False.
    """

    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    try:
        client.get_table(
            table_ref
        )

        return True
    except NotFound:
        return False

def create_table(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    table_config: dict
) -> None:
    """
    Create a BigQuery table.
    """

    table_id = table_config["id"]

    console.print_step("Creating table", table_id)

    if table_exists(client, project_id, dataset_id, table_id):
        console.print_info("Already exists. Skipping creation.")
        return

    table = bigquery.Table(
        f"{project_id}.{dataset_id}.{table_id}"
    )
    table.description = table_config.get(
        "description"
    )
    table.schema = load_schema(
        table_config["schema"]
    )
    partition = table_config.get(
        "partition"
    )
    if partition:
        table.time_partitioning = (
            bigquery.TimePartitioning(
                field=partition["field"]
            )
        )
    clustering = table_config.get(
        "clustering"
    )
    if clustering:
        table.clustering_fields = clustering
    labels = table_config.get(
        "labels"
    )
    if labels:
        table.labels = labels

    try:

        client.create_table(
            table
        )

        console.print_success()
    except Exception as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def create_tables(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
) -> None:
    """
    Create all configured BigQuery tables.
    """

    if not TABLES_DIR.exists():
        return

    for yaml_file in sorted(TABLES_DIR.glob("*.yaml")):
        table_config = load_yaml(
            "infrastructure",
            "gcp",
            "bigquery",
            "tables",
            yaml_file.name,
        )

        create_table(
            client,
            project_id,
            dataset_id,
            table_config["table"],
        )

def main() -> None:
    console.print_header("Creating BigQuery tables")

    gcp_config = load_yaml(
        "infrastructure",
        "gcp",
        "gcp.yaml"
    )
    dataset_config = load_yaml(
        "infrastructure",
        "gcp",
        "bigquery.yaml"
    )

    project_id = gcp_config["project"]["project_id"]
    dataset_id = dataset_config["dataset"]["id"]

    client = bigquery.Client(
        project=project_id
    )

    create_tables(client, project_id, dataset_id)

    console.print_footer("BigQuery tables")

if __name__ == "__main__":
    main()