"""
create_cloud_storage.py

Create the Google Cloud storage bucket required by the project.
"""

from mlb_data.utils.config_loader import load_yaml
from mlb_data.infrastructure.gcp.gcloud import run_gcloud, GCloudError
from mlb_data.utils import console
from pathlib import Path
import json
import tempfile

def bucket_exists(
    project_id: str,
    bucket_name: str
) -> bool:
    """
    Check whether a Cloud Storage bucket exists.

    Parameters
    ----------
    project_id : str
        Google Cloud project ID.

    bucket_name : str
        Cloud Storage bucket name.

    Returns
    -------
    bool
        True if the bucket exists, otherwise False.
    """

    try:
        run_gcloud(
            "storage",
            "buckets",
            "describe",
            f"gs://{bucket_name}",
            project=project_id
        )

        return True
    except GCloudError:
        return False

def create_bucket(
    project_id: str,
    region: str,
    bucket: dict
) -> None:
    """
    Create a Cloud Storage bucket.
    """

    bucket_name = bucket["name"]

    console.print_step("Creating bucket", bucket_name)

    if bucket_exists(project_id, bucket_name):
        console.print_info("Already exists. Skipping creation.")
        return

    command = [
        "storage",
        "buckets",
        "create",
        f"gs://{bucket_name}",
        f"--location={region}",
        f"--default-storage-class={bucket['storage_class']}",
    ]

    if bucket["uniform_bucket_level_access"]:
        command.append("--uniform-bucket-level-access")

    try:
        run_gcloud(
            *command,
            project=project_id
        )

        console.print_success()
    except GCloudError as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def configure_versioning(
    project_id: str,
    bucket: dict
) -> None:
    """
    Configure versioning for a Google Cloud storage bucket.
    """
    bucket_name = bucket["name"]
    console.print_step("Configuring versioning for bucket", bucket_name)

    command = [
        "storage",
        "buckets",
        "update",
        f"gs://{bucket_name}"
    ]

    if bucket["versioning"]:
        command.append("--versioning")
    else:
        command.append("--no-versioning")

    run_gcloud(
        *command,
        project=project_id
    )

    console.print_success()

def configure_lifecycle(
    project_id: str,
    bucket: dict
) -> None:
    """
    Configure lifecycle rules for a Google Cloud storage bucket.
    """
    bucket_name = bucket["name"]
    console.print_step("Configuring lifecycle for bucket", bucket_name)
    lifecycle = bucket.get("lifecycle")

    if lifecycle is None:
        return

    lifecycle_policy = {
        "rule": [
            {
                "action": {
                    "type": "Delete"
                },
                "condition": {
                    "age": lifecycle["delete_after_days"],
                    "matchesPrefix": lifecycle["prefixes"]
                }
            }
        ]
    }

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8"
    ) as file:

        json.dump(
            lifecycle_policy,
            file,
            indent=4
        )

        lifecycle_file = Path(file.name)

    try:
        run_gcloud(
            "storage",
            "buckets",
            "update",
            f"gs://{bucket['name']}",
            f"--lifecycle-file={lifecycle_file}",
            project=project_id
        )

        console.print_success()
    finally:
        lifecycle_file.unlink(missing_ok=True)

def main() -> None:
    console.print_header("Create Cloud Storage Bucket")

    gcp_config = load_yaml(
            "infrastructure",
            "gcp",
            "gcp.yaml"
        )
    storage_config = load_yaml(
            "infrastructure",
            "gcp",
            "cloud_storage.yaml"
        )

    project_id = gcp_config["project"]["project_id"]
    region = gcp_config["project"]["region"]
    bucket = storage_config["bucket"]

    create_bucket(
        project_id,
        region,
        bucket
    )
    configure_versioning(
        project_id,
        bucket
    )
    configure_lifecycle(
        project_id,
        bucket
    )

    console.print_footer("Create Cloud Storage Bucket")

if __name__ == "__main__":
    main()