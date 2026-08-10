from mlb_data.infrastructure.databricks.sql_client import managed_connection
from mlb_data.infrastructure.databricks.create_catalog import main as create_catalog

def main() -> None:
    print("="*30)
    print("Starting Databricks deployment...\n")

    create_catalog()

    managed_connection.close_connection()

    print("\nDatabricks deployment completed successfully.")
    print("="*30)

if __name__ == "__main__":
    main()