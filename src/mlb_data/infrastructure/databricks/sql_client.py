"""
sql_client.py

Provides a reusable connection to a Databricks SQL Warehouse.
"""

from databricks import sql
from mlb_data.utils.config_loader import load_yaml

class DatabricksSQLConnection:
    def __init__(self) -> None:
        self.config = load_yaml(
            "infrastructure",
            "databricks",
            "databricks.yaml",
        )

        self._connection = None

    def get_connection(self):
        """
        Return the existing SQL connection or create a new one.
        """

        if self._connection is None:
            self._connection = sql.connect(
                server_hostname=self.config["sql_warehouse"]["server_hostname"],
                http_path=self.config["sql_warehouse"]["http_path"],
                auth_type="databricks-oauth",
            )

        return self._connection

    def close_connection(self) -> None:
        """
        Close the SQL connection if it is open.
        """

        if self._connection is not None:
            self._connection.close()
            self._connection = None

managed_connection = DatabricksSQLConnection()