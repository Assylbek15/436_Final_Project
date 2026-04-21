from dotenv import load_dotenv
load_dotenv()

import os
from azure.storage.blob import BlobServiceClient

conn_str  = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
container = os.environ.get("AZURE_STORAGE_CONTAINER", "documents")

if not conn_str:
    print("ERROR: AZURE_STORAGE_CONNECTION_STRING not set in .env")
    exit(1)

print(f"Container : {container}")
print("Connecting to Azure Blob Storage...")

try:
    client = BlobServiceClient.from_connection_string(conn_str)
    account = client.get_account_information()
    print(f"SUCCESS — connected! Account kind: {account.get('account_kind', 'ok')}")

    # Create container if it doesn't exist
    cc = client.get_container_client(container)
    if not cc.exists():
        cc.create_container()
        print(f"Created container: '{container}'")
    else:
        print(f"Container '{container}' already exists")

    # Upload a test file
    blob = client.get_blob_client(container, "test.txt")
    blob.upload_blob(b"Hello from Digital Document Inspector!", overwrite=True)
    print(f"Test file uploaded: {blob.url}")

except Exception as e:
    print(f"FAILED: {e}")
