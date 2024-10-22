import logging

import azure.functions as func
import azurefunctions.extensions.bindings.blob as blob

bp = func.Blueprint()

@bp.blob_trigger(
    arg_name="client",
    path="upload-newsvideos/{name}",
    connection="BlobTrigger",
    # source="LogsAndContainerScan",
)
def blob_trigger(client: blob.BlobClient):
    logging.info(
        f"Python blob trigger function processed blob \n"
        f"Properties: {client.get_blob_properties()}\n"
        f"Blob content head: {client.download_blob().read(size=1)}"
    )
