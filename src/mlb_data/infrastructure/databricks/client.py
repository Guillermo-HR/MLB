"""
Databricks client.

Provides a configured Databricks WorkspaceClient.
"""

from databricks.sdk import WorkspaceClient
from mlb_data.utils.config_loader import load_yaml

WORKSPACE_CLIENT = None

def get_workspace_client() -> WorkspaceClient:
    """
    Create and return a Databricks Workspace client.

    Returns:
        WorkspaceClient: Authenticated Databricks client.
    """
    config = load_yaml(
            "infrastructure",
            "databricks",
            "databricks.yaml"
        )

    return WorkspaceClient(
        profile=config["profile"]
    )