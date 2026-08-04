from mlb_data.utils.config_loader import load_yaml
from mlb_data.utils.gcloud import run_gcloud, GCloudError
from pathlib import Path
import json
import tempfile

def create_bucket(project_id: str, region: str, bucket: dict,) -> None:
    bucket_name = bucket["name"]
    print(f"create bucket: {bucket_name}")

    try:
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

        run_gcloud(
            *command,
            project=project_id,
        )

        print(f"Bucket {bucket_name} created successfully.")
    except GCloudError as error:
        if "already exists" in str(error):
            print(f"Bucket {bucket_name} already exists.")
        else:
            raise

def configure_versioning(project_id: str,bucket: dict,) -> None:
    bucket_name = bucket["name"]

    print(f"Configuring versioning for bucket: {bucket_name}")

    command = [
        "storage",
        "buckets",
        "update",
        f"gs://{bucket_name}",
    ]

    if bucket["versioning"]:
        command.append("--versioning")
    else:
        command.append("--no-versioning")

    run_gcloud(
        *command,
        project=project_id,
    )

    print(f"Configured versioning for bucket: {bucket_name}")

def configure_lifecycle(project_id: str,bucket: dict,) -> None:
    bucket_name = bucket["name"]
    print(f"Configuring lifecycle for bucket: {bucket_name}")
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
                    "matchesPrefix": lifecycle["prefixes"],
                },
            }
        ]
    }

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as file:

        json.dump(
            lifecycle_policy,
            file,
            indent=4,
        )

        lifecycle_file = Path(file.name)

    try:
        run_gcloud(
            "storage",
            "buckets",
            "update",
            f"gs://{bucket['name']}",
            f"--lifecycle-file={lifecycle_file}",
            project=project_id,
        )

        print(f"Configured lifecycle for bucket: {bucket['name']}")

    finally:
        lifecycle_file.unlink(missing_ok=True)


def main() -> None:
    gcp_config = load_yaml("infrastructure","gcp.yaml",)

    storage_config = load_yaml("infrastructure","cloud_storage.yaml",)

    project_id = gcp_config["project"]["project_id"]
    region = gcp_config["project"]["region"]

    bucket = storage_config["bucket"]

    create_bucket(
        project_id,
        region,
        bucket,
    )
    configure_versioning(
        project_id,
        bucket,
    )
    configure_lifecycle(
        project_id,
        bucket,
    )

    print("\nBucket successfully processed.")

if __name__ == "__main__":
    main()