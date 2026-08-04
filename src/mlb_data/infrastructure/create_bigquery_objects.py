from pathlib import Path
from google.cloud import bigquery
from mlb_data.utils.config_loader import load_yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TABLES_DIR = (
    PROJECT_ROOT
    / "config"
    / "infrastructure"
    / "big_query"
    / "tables"
)

def load_schema(schema: list[dict]) -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField(
            name=field["name"],
            field_type=field["type"],
            mode=field.get("mode", "NULLABLE"),
            description=field.get("description"),
        )
        for field in schema
    ]

def create_table(client: bigquery.Client, project_id: str, dataset_id: str, table_config: dict,) -> None:
    table_id = table_config["id"]

    print(f"Creating table: {table_id}")

    table = bigquery.Table(
        f"{project_id}.{dataset_id}.{table_id}"
    )

    table.description = table_config.get("description")

    table.schema = load_schema(
        table_config["schema"]
    )

    partition = table_config.get("partition")

    if partition:

        table.time_partitioning = (
            bigquery.TimePartitioning(
                field=partition["field"]
            )
        )

    clustering = table_config.get("clustering")

    if clustering:

        table.clustering_fields = clustering

    labels = table_config.get("labels")

    if labels:

        table.labels = labels

    client.create_table(
        table,
        exists_ok=True,
    )

    print(f"Table {table_id} created successfully.")

def create_tables(client: bigquery.Client, project_id: str, dataset_id: str,) -> None:
    if not TABLES_DIR.exists():
        return

    print("\nCreating tables...\n")

    for yaml_file in sorted(TABLES_DIR.glob("*.yaml")):

        config = load_yaml("infrastructure", "big_query", "tables",yaml_file.name,)

        create_table(
            client,
            project_id,
            dataset_id,
            config["table"],
        )

def main() -> None:

    gcp_config = load_yaml("infrastructure","gcp.yaml",)

    dataset_config = load_yaml("infrastructure","big_query.yaml",)

    project_id = gcp_config["project"]["project_id"]

    dataset_id = dataset_config["dataset"]["id"]

    client = bigquery.Client(project=project_id,)

    create_tables(
        client,
        project_id,
        dataset_id,
    )

    print("\nBigQuery objects successfully processed.")


if __name__ == "__main__":
    main()