"""
create_bigquery_dataset.py

Create the BigQuery dataset required by the project.
"""

from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils.gcloud import run_bq, GCloudError
from mlb_data.utils import console

def dataset_exists(
    project_id: str,
    dataset_id: str
) -> bool:
    """
    Check whether a BigQuery dataset exists.

    Parameters
    ----------
    project_id : str
        Google Cloud project ID.

    dataset_id : str
        BigQuery dataset ID.

    Returns
    -------
    bool
        True if the dataset exists, otherwise False.
    """

    try:
        run_bq(
            "show",
            "--dataset",
            dataset_id,
            project=project_id
        )

        return True
    except GCloudError:
        return False

def create_dataset(
    project_id: str, 
    region: str, 
    dataset: dict
) -> None:
    """
    Create a BigQuery dataset.
    """

    dataset_id = dataset["id"]

    console.print_step("Creating dataset", dataset_id)

    if dataset_exists(project_id, dataset_id):
        console.print_info("Already exists. Skipping creation.")
        return

    try:
        run_bq(
            "mk",
            "--dataset",
            f"--location={region}",
            f"--description={dataset['description']}",
            dataset_id,
            project=project_id
        )

        console.print_success()
    except GCloudError as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def main() -> None:
    console.print_header("Create BigQuery Dataset")

    gcp_config = load_yaml(
            "infrastructure",
            "gcp",
            "gcp.yaml"
        )
    bq_config = load_yaml(
            "infrastructure",
            "gcp",
            "bigquery.yaml"
        )

    project_id = gcp_config["project"]["project_id"]
    region = gcp_config["project"]["region"]

    create_dataset(
        project_id,
        region,
        bq_config["dataset"]
    )

    console.print_footer("Create BigQuery Dataset")

if __name__ == "__main__":
    main()