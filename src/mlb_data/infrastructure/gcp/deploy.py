from mlb_data.infrastructure.gcp.enable_services import main as enable_services
from mlb_data.infrastructure.gcp.create_service_accounts import main as create_service_accounts
from mlb_data.infrastructure.gcp.create_cloud_storage import main as create_cloud_storage
from mlb_data.infrastructure.gcp.create_bigquery_dataset import main as create_bigquery_dataset
from mlb_data.infrastructure.gcp.create_bigquery_objects import main as create_bigquery_objects

def main() -> None:
    print("="*30)
    print("Starting GCP deployment...\n")

    enable_services()
    create_service_accounts()
    create_cloud_storage()
    create_bigquery_dataset()
    create_bigquery_objects()

    print("\nGCP deployment completed successfully.")
    print("="*30)
    
if __name__ == "__main__":
    main()