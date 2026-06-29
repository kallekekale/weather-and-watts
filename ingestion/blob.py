from datetime import datetime, UTC
from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, BLOB_CONTAINER


def upload_raw(source, content, ext):
    """Archive a raw API response to blob storage (the bronze layer).

    Writes to raw/<source>/<YYYY>/<MM>/<DD>/<source>_<timestamp>.<ext> so the
    untouched response is always recoverable for reprocessing. Returns the
    blob path it was written to."""
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise RuntimeError(
            "AZURE_STORAGE_CONNECTION_STRING is not set; cannot archive raw data"
        )

    fetched_at = datetime.now(UTC)
    blob_name = (
        f"{source}/{fetched_at:%Y/%m/%d}/{source}_{fetched_at:%Y%m%dT%H%M%SZ}.{ext}"
    )
    service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container = service.get_container_client(BLOB_CONTAINER)
    container.upload_blob(name=blob_name, data=content, overwrite=True)
    return blob_name
