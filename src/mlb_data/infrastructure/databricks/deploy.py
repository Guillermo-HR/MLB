from mlb_data.infrastructure.databricks.sql_client import managed_connection
from mlb_data.infrastructure.databricks.create_service_principals import main as create_service_principals
from mlb_data.infrastructure.databricks.create_catalog import main as create_catalog
from mlb_data.infrastructure.databricks.create_schemas import main as create_schemas

def main() -> None:
    print("="*30)
    print("Starting Databricks deployment...\n")

    create_service_principals()
    create_catalog()
    create_schemas()

    managed_connection.close_connection()

    print("\nDatabricks deployment completed successfully.")
    print("="*30)

if __name__ == "__main__":
    main()