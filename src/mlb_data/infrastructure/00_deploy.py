from mlb_data.infrastructure.enable_services import main as enable_services_main
from mlb_data.infrastructure.create_service_accounts import main as create_service_accounts_main
from mlb_data.infrastructure.create_cloud_storage import main as create_cloud_storage_main
from mlb_data.infrastructure.create_bigquery_dataset import main as create_bigquery_dataset_main
from mlb_data.infrastructure.create_bigquery_objects import main as create_bigquery_objects_main

def main() -> None:
    enable_services_main()
    create_service_accounts_main()
    create_cloud_storage_main()
    create_bigquery_dataset_main()
    create_bigquery_objects_main()
    
if __name__ == "__main__":
    main()