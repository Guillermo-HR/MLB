"""
assign_iam.py

Assign IAM roles to Google Cloud service accounts.
"""

import json
from mlb_data.utils import console
from mlb_data.utils.config_loader import load_yaml
from mlb_data.infrastructure.gcp.gcloud import run_gcloud, run_bq, GCloudError
from google.cloud import bigquery

def get_service_account_email(
    project_id: str,
    service_account_id: str,
) -> str:
    """
    Build the email address of a service account.
    """

    return (
        f"{service_account_id}"
        f"@{project_id}.iam.gserviceaccount.com"
    )

def storage_binding_exists(
    project_id: str,
    bucket_name: str,
    member: str,
    role: str,
) -> bool:
    """
    Check whether a Cloud Storage IAM binding already exists.
    """

    result = run_gcloud(
        "storage",
        "buckets",
        "get-iam-policy",
        f"gs://{bucket_name}",
        "--format=json",
        project=project_id,
    )

    policy = json.loads(result.stdout)

    for binding in policy.get("bindings", []):
        if binding.get("role") != role:
            continue
        if member in binding.get("members", []):
            return True

    return False

def bigquery_binding_exists(
    client: bigquery.Client,
    dataset_id: str,
    service_account_email: str,
    role: str,
) -> bool:
    """
    Check whether a service account already has a role
    on a BigQuery dataset.
    """

    role_mapping = {
        "roles/bigquery.dataViewer": "READER",
        "roles/bigquery.dataEditor": "WRITER",
        "roles/bigquery.dataOwner": "OWNER",
    }
    dataset_role = role_mapping.get(role)
    dataset = client.get_dataset(dataset_id)

    if dataset_role is None:
        raise ValueError(
            f"Unsupported BigQuery dataset role: {role}"
        )

    for entry in dataset.access_entries:
        if entry.role != dataset_role:
            continue
        if entry.entity_type != "userByEmail":
            continue
        if entry.entity_id == service_account_email:
            return True

    return False

def project_iam_binding_exists(
    project_id: str,
    member: str,
    role: str,
) -> bool:
    """
    Check whether an IAM role is already assigned
    to a member at project level.
    """

    result = run_gcloud(
        "projects",
        "get-iam-policy",
        project_id,
        "--format=json"
    )

    policy = json.loads(result.stdout)

    for binding in policy.get("bindings", []):
        if binding.get("role") != role:
            continue
        if member in binding.get("members", []):
            return True

    return False

def assign_storage_role(
    project_id: str,
    bucket_name: str,
    service_account_email: str,
    role: str,
) -> None:
    """
    Assign an IAM role to a service account on a Cloud Storage bucket.
    """

    member = f"serviceAccount:{service_account_email}"

    console.print_step("Assigning Storage role",f"{role}: {service_account_email}")

    if storage_binding_exists(
        project_id,
        bucket_name,
        member,
        role,
    ):
        console.print_info("Already exists. Skipping.")
        return
    try:
        run_gcloud(
            "storage",
            "buckets",
            "add-iam-policy-binding",
            f"gs://{bucket_name}",
            f"--member={member}",
            f"--role={role}",
            project=project_id,
        )

        console.print_success()
    except GCloudError as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def assign_bigquery_role(
    client: bigquery.Client,
    dataset_id: str,
    service_account_email: str,
    role: str,
) -> None:
    """
    Assign a BigQuery dataset role to a service account.
    """

    role_mapping = {
        "roles/bigquery.dataViewer": "READER",
        "roles/bigquery.dataEditor": "WRITER",
        "roles/bigquery.dataOwner": "OWNER",
    }
    dataset_role = role_mapping.get(role)

    console.print_step("Assigning BigQuery role",f"{role}: {service_account_email}")

    if bigquery_binding_exists(
        client,
        dataset_id,
        service_account_email,
        role,
    ):
        console.print_info(
            "Already exists. Skipping."
        )
        return

    if dataset_role is None:
        raise ValueError(
            f"Unsupported BigQuery dataset role: {role}"
        )
    
    try:
        dataset = client.get_dataset(dataset_id)

        access_entry = bigquery.AccessEntry(
            role=dataset_role,
            entity_type="userByEmail",
            entity_id=service_account_email,
        )

        dataset.access_entries = [
            *dataset.access_entries,
            access_entry,
        ]

        client.update_dataset(
            dataset,
            ["access_entries"],
        )

        console.print_success()
    except Exception as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def assign_project_role(
    project_id: str,
    service_account_email: str,
    role: str,
) -> None:
    """
    Assign an IAM role to a service account at project level.
    """

    member = f"serviceAccount:{service_account_email}"

    console.print_step("Assigning project role",f"{role}: {service_account_email}")

    if project_iam_binding_exists(
        project_id,
        member,
        role,
    ):
        console.print_info(
            "Already exists. Skipping."
        )
        return

    try:
        run_gcloud(
            "projects",
            "add-iam-policy-binding",
            project_id,
            f"--member={member}",
            f"--role={role}",
        )

        console.print_success()
    except GCloudError as error:
        console.print_failed()
        console.print_error(str(error))
        raise

def assign_storage_permissions(
    project_id: str,
    service_accounts: dict,
    iam_config: dict,
) -> None:
    """
    Assign Cloud Storage IAM roles.
    """

    storage_binding = iam_config["bindings"]["cloud_storage"]
    bucket_name = storage_binding["bucket"]

    for account_name, binding in storage_binding["members"].items():
        if account_name not in service_accounts:
            raise KeyError(
                f"Service account '{account_name}' "
                f"not found in service_accounts.yaml."
            )

        service_account_id = service_accounts[account_name]["id"]
        service_account_email = (
            get_service_account_email(
                project_id,
                service_account_id
            )
        )

        assign_storage_role(
            project_id,
            bucket_name,
            service_account_email,
            binding["role"]
        )

def assign_bigquery_dataset_permissions(
    client: bigquery.Client,
    project_id: str,
    service_accounts: dict,
    iam_config: dict,
) -> None:
    """
    Assign IAM roles at BigQuery dataset level.
    """

    bigquery_binding = iam_config["bindings"]["bigquery"]
    dataset_id = bigquery_binding["dataset"]

    for account_name, binding in (
        bigquery_binding["dataset_members"].items()
    ):
        if account_name not in service_accounts:
            raise KeyError(
                f"Service account '{account_name}' "
                f"not found in service_accounts.yaml."
            )

        service_account_id = (
            service_accounts[account_name]["id"]
        )
        service_account_email = (
            get_service_account_email(
                project_id,
                service_account_id,
            )
        )
        roles = binding["roles"]

        for role in roles:
            assign_bigquery_role(
                client,
                dataset_id,
                service_account_email,
                role,
            )

def assign_bigquery_project_permissions(
    project_id: str,
    service_accounts: dict,
    iam_config: dict,
) -> None:
    """
    Assign IAM roles at Google Cloud project level.
    """

    bigquery_binding = iam_config["bindings"]["bigquery"]

    for account_name, binding in (
        bigquery_binding["project_members"].items()
    ):
        if account_name not in service_accounts:
            raise KeyError(
                f"Service account '{account_name}' "
                f"not found in service_accounts.yaml."
            )

        service_account_id = (
            service_accounts[account_name]["id"]
        )

        service_account_email = (
            get_service_account_email(
                project_id,
                service_account_id,
            )
        )

        roles = binding["roles"]

        for role in roles:
            assign_project_role(
                project_id,
                service_account_email,
                role,
            )

def main() -> None:

    console.print_header("Assign Google Cloud IAM permissions")

    gcp_config = load_yaml(
        "infrastructure",
        "gcp",
        "gcp.yaml"
    )
    service_accounts_config = load_yaml(
        "infrastructure",
        "gcp",
        "service_accounts.yaml"
    )
    iam_config = load_yaml(
        "infrastructure",
        "gcp",
        "iam.yaml"
    )

    project_id = gcp_config["project"]["project_id"]
    service_accounts = service_accounts_config["service_accounts"]

    client = bigquery.Client(
        project=project_id,
    )

    assign_storage_permissions(
        project_id,
        service_accounts,
        iam_config
    )
    assign_bigquery_dataset_permissions(
        client,
        project_id,
        service_accounts,
        iam_config,
    )
    assign_bigquery_project_permissions(
        project_id,
        service_accounts,
        iam_config,
    )

    console.print_footer("Google Cloud IAM permissions")

if __name__ == "__main__":
    main()