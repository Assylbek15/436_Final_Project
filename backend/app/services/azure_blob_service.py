import io
from PIL import Image
from azure.storage.blob import BlobServiceClient, ContentSettings


class AzureBlobService:
    def __init__(self, connection_string: str, container: str):
        self._client    = BlobServiceClient.from_connection_string(connection_string)
        self._container = container
        self._account   = self._client.account_name
        self._ensure_container()

    def _ensure_container(self):
        cc = self._client.get_container_client(self._container)
        if not cc.exists():
            cc.create_container(public_access="blob")
        else:
            cc.set_container_access_policy(signed_identifiers={}, public_access="blob")

    def upload_image(self, pil_image: Image.Image, blob_name: str) -> str:
        buf = io.BytesIO()
        pil_image.save(buf, format="JPEG")
        buf.seek(0)
        blob = self._client.get_blob_client(self._container, blob_name)
        blob.upload_blob(
            buf,
            overwrite=True,
            content_settings=ContentSettings(content_type="image/jpeg"),
        )
        return self._public_url(blob_name)

    def upload_bytes(self, data: bytes, blob_name: str, content_type: str) -> str:
        blob = self._client.get_blob_client(self._container, blob_name)
        blob.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return self._public_url(blob_name)

    def _public_url(self, blob_name: str) -> str:
        return f"https://{self._account}.blob.core.windows.net/{self._container}/{blob_name}"
