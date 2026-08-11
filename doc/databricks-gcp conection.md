# Connecting Databricks to GCP

Because the proyect uses Databricks Free Edition with AWS, the connection to GCP is not possible. To solve it you have to add the keys from the service acounts to Databricks secrets.
## Creating a service account key
After executing the infrastructure deployment you have to go to AIM and administratin > service accounts > mlb-databricks-sa@<PROJECT_ID>.iam.gserviceaccount.com > keys and create a JSON key. The result will be a file with this kind of content:
```
{
        "type": "service_account",
        "project_id": "<PROJECT_ID>",
        "private_key_id": "<PRIVATE_KEY_ID>",
        "private_key": "<PRIVATE_KEY>",
        "client_email": "<CLIENT_EMAIL>",
        "client_id": "<CLIENT_ID>",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "<CLIENT_X509_CERT_URL>"
        "universe_domain": "googleapis.com"
}
```
## Creating a secret scope
In Databricks, you have to create a secret scope to store the service account key.
```
databricks secrets create-scope mlb-gcp
```
To validate that the secret scope was created, you can run:
```
databricks secrets list-scopes
```
## Adding keys to the secret scope
To upload the service account key to the secret scope, run the script below, replacing `<PATH_TO_JSON_KEY>` with the path to the JSON key file you downloaded from GCP.
```
cd src/mlb_data/infrastructure/databricks/load_gcp_secrets.py

python load_gcp_secrets.py "<PATH_TO_JSON_KEY>"
```