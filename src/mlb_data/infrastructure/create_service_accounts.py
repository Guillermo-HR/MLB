from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils.gcloud import run_gcloud, GCloudError

def create_service_account(project_id: str,service_account: dict,) -> None:
    account_id = service_account["id"]
    display_name = service_account["display_name"]
    description = service_account.get("description", "")

    print(f"Account: {account_id}")

    try:
        run_gcloud(
            "iam",
            "service-accounts",
            "create",
            account_id,
            f"--display-name={display_name}",
            f"--description={description}",
            project=project_id,
        )

        print(f"Service account {account_id} created successfully.")

    except GCloudError as error:

        if "already exists" in str(error):
            print(f"Service account {account_id} already exists.")
        else:
            raise

def main() -> None:
    gcp_config = load_yaml("infrastructure", "gcp.yaml")
    sa_config = load_yaml("infrastructure", "service_accounts.yaml")

    project_id = gcp_config["project"]["project_id"]

    for name, service_account in sa_config["service_accounts"].items():
        create_service_account(
            project_id,
            service_account,
        )

    print("\nService accounts successfully processed.")

if __name__ == "__main__":
    main()