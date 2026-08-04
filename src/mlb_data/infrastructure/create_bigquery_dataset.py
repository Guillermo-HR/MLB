from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils.gcloud import run_bq, GCloudError


def create_dataset(project_id: str, region: str, dataset: dict,) -> None:
    dataset_id = dataset["id"]

    print(f"Creating dataset: {dataset_id}")

    try:
        run_bq(
            "mk",
            "--dataset",
            f"--location={region}",
            dataset_id,
            project=project_id,
        )

        print(f"Dataset {dataset_id} created successfully.")

    except GCloudError as error:

        if "already exists" in str(error).lower():
            print(f"Dataset {dataset_id} already exists")
        else:
            raise

def main() -> None:
    gcp_config = load_yaml("infrastructure","gcp.yaml",)

    bq_config = load_yaml("infrastructure", "big_query.yaml",)

    project_id = gcp_config["project"]["project_id"]
    region = gcp_config["project"]["region"]

    create_dataset(
        project_id,
        region,
        bq_config["dataset"],
    )

    print("\nDataset successfully processed.")


if __name__ == "__main__":
    main()