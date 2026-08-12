from mlb_data.infrastructure.gcp.deploy import main as gcp_deploy
from mlb_data.infrastructure.databricks.deploy import main as databricks_deploy

def main() -> None:
    print("="*50)
    print("Starting infrastructure deployment...\n")

    gcp_deploy()
    databricks_deploy()

    print("\nInfrastructure deployment completed successfully.")
    print("="*50)

if __name__ == "__main__":
    main()