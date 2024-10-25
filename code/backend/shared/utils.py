import hashlib
import logging
import os
import shutil
import uuid
from urllib.parse import unquote

from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobLeaseClient, BlobServiceClient
from azure.storage.blob import BlobProperties


def get_guid(seed: str) -> str:
    """Generate a guid based on a string seed.

    seed (str): Specifies a string used as a seed.
    RETURNS (str): Returns a guid as string.
    """
    seed_hex = hashlib.md5(seed.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=seed_hex, version=4))


def get_azure_credential(
    managed_identity_client_id: str = None,
) -> DefaultAzureCredential:
    """Creates a default azure crendetial used for authentication.

    managed_identity_client_id (str): Specifies the client id of a managed identity.
    RETURNS (str): Returns a default azure credential.
    """
    if managed_identity_client_id is None:
        return DefaultAzureCredential()
    else:
        return DefaultAzureCredential(
            managed_identity_client_id=managed_identity_client_id,
        )

async def get_blob_properties(
    storage_domain_name: str,
    storage_container_name: str,
    storage_blob_name: str,
    managed_identity_client_id: str = None,
) -> BlobProperties:
    """Copy file from source blob storage container async to sink blob storage container.

    storage_domain_name (str): The domain name of the storage account to which the file will be copied.
    storage_container_name (str): The container name of the storage account.
    storage_blob_name (str): The blob name of the storage account.
    managed_identity_client_id (str): Specifies the managed identity client id used for auth.
    RETURNS (BlobProperties): Returns the properties of the blob.
    """
    logging.info(
        f"Get properties for blob: 'https://{storage_domain_name}/{storage_container_name}/{storage_blob_name}'."
    )

    # Create credentials
    credential = get_azure_credential(
        managed_identity_client_id=managed_identity_client_id
    )

    # Copy blob file
    async with BlobServiceClient(
        account_url=f"https://{storage_domain_name}",
        credential=credential,
    ) as blob_service_client:
        blob_client = blob_service_client.get_blob_client(
            container=storage_container_name,
            blob=storage_blob_name,
        )
        blob_properties = await blob_client.get_blob_properties()

    return blob_properties


async def copy_blob_from_url(
    source_url: str,
    sink_storage_domain_name: str,
    sink_storage_container_name: str,
    sink_storage_blob_name: str,
    managed_identity_client_id: str = None,
) -> str:
    """Copy file from source blob storage container async to sink blob storage container.

    source_url (str): The url of the source file.
    sink_storage_domain_name (str): The domain name of the storage account to which the file will be copied.
    sink_storage_container_name (str): The container name of the storage account.
    sink_storage_blob_name (str): The blob name of the storage account.
    managed_identity_client_id (str): Specifies the managed identity client id used for auth.
    RETURNS (str): Returns the url of the destination blob.
    """
    logging.info(
        f"Start copying file source '{source_url}' to sink 'https://{sink_storage_domain_name}/{sink_storage_container_name}/{sink_storage_blob_name}'."
    )

    # Create credentials
    credential = get_azure_credential(
        managed_identity_client_id=managed_identity_client_id
    )

    # Copy blob file
    async with BlobServiceClient(
        account_url=f"https://{sink_storage_domain_name}",
        credential=credential,
    ) as blob_service_client:
        sink_blob_client = blob_service_client.get_blob_client(
            container=sink_storage_container_name,
            blob=sink_storage_blob_name,
        )
        await sink_blob_client.upload_blob_from_url(
            source_url=source_url, overwrite=True
        )

    return sink_blob_client.url


async def copy_blob(
    storage_domain_name: str,
    source_storage_container_name: str,
    source_storage_blob_name: str,
    sink_storage_container_name: str,
    sink_storage_blob_name: str,
    delete_source: bool = True,
    managed_identity_client_id: str = None,
) -> str:
    """Copy file from source blob storage container async to sink blob storage container.

    storage_domain_name (str): The domain name of the storage account.
    source_storage_container_name (str): The container name of the storage account.
    source_storage_blob_name (str): The blob name of the storage account.
    sink_storage_container_name (str): The container name of the storage account.
    sink_storage_blob_name (str): The blob name of the storage account.
    delete_source (bool): Specifies whether the source blob should be removed after the successful copy activity.
    managed_identity_client_id (str): Specifies the managed identity client id used for auth.
    RETURNS (str): Returns the url of the destination blob.
    """
    logging.info(
        f"Start copying file source 'https://{storage_domain_name}/{source_storage_container_name}/{source_storage_blob_name}' to sink 'https://{storage_domain_name}/{sink_storage_container_name}/{sink_storage_blob_name}'."
    )

    # Create credentials
    credential = get_azure_credential(
        managed_identity_client_id=managed_identity_client_id
    )

    # Copy blob file
    async with BlobServiceClient(
        account_url=f"https://{storage_domain_name}",
        credential=credential,
    ) as blob_service_client:
        # Create blob clients
        source_blob_client = blob_service_client.get_blob_client(
            container=source_storage_container_name,
            blob=source_storage_blob_name,
        )
        sink_blob_client = blob_service_client.get_blob_client(
            container=sink_storage_container_name,
            blob=sink_storage_blob_name,
        )

        # Aquire lease
        lease = BlobLeaseClient(
            client=source_blob_client,
        )
        await lease.acquire(lease_duration=-1)

        # Copy blob
        await sink_blob_client.start_copy_from_url(
            source_url=source_blob_client.url,
            requires_sync=True,
        )

        # Delete source blob
        if delete_source:
            await source_blob_client.delete_blob(
                delete_snapshots="include", lease=lease
            )
        else:
            await lease.release()
    return sink_blob_client.url


async def download_blob(
    file_path: str,
    storage_domain_name: str,
    storage_container_name: str,
    storage_blob_name: str,
    managed_identity_client_id: str = None,
) -> str:
    """Download file from blob storage async to local storage.

    file_path (str): The file path to which the file will be downloaded.
    storage_domain_name (str): The domain name of the storage account.
    storage_container_name (str): The container name of the storage account.
    storage_blob_name (str): The blob name of the storage account.
    managed_identity_client_id (str): Specifies the managed identity client id used for auth.
    RETURNS (str): The file path to which the file was downloaded.
    """
    logging.info(f"Start downloading file from blob storage to '{file_path}'.")

    # Preprocess storage blob name
    storage_blob_name_cleansed = unquote(storage_blob_name)
    logging.debug(
        f"Storage Details: Domain='{storage_domain_name}', Container='{storage_container_name}', Blob='{storage_blob_name_cleansed}'."
    )

    # Create credentials
    credential = get_azure_credential(
        managed_identity_client_id=managed_identity_client_id
    )

    # Create directory
    head, _ = os.path.split(file_path)
    if not os.path.exists(head):
        os.makedirs(head)

    # Create client
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_domain_name}", credential=credential
    )
    blob_client = blob_service_client.get_blob_client(
        container=storage_container_name, blob=storage_blob_name_cleansed
    )

    # Download blob
    with open(file=file_path, mode="wb") as sample_blob:
        download_stream = await blob_client.download_blob()
        data = await download_stream.readall()
        sample_blob.write(data)

    logging.info(f"Finished downloading file from blob storage to '{file_path}'.")

    # Return file path of downloaded blob
    return file_path


async def upload_blob(
    file_path: str,
    storage_domain_name: str,
    storage_container_name: str,
    storage_blob_name: str,
    managed_identity_client_id: str = None,
) -> str:
    """Upload file to blob storage async from local storage.

    file_path (str): The file path to which the file will be downloaded.
    storage_domain_name (str): The domain name of the storage account.
    storage_container_name (str): The container name of the storage account.
    storage_blob_name (str): The blob name of the storage account.
    managed_identity_client_id (str): Specifies the managed identity client id used for auth.
    RETURNS (str): The url of the uploaded blob.
    """
    logging.info(f"Start uploading file '{file_path}' to blob storage.")

    # Preprocess storage blob name
    storage_blob_name_cleansed = unquote(storage_blob_name)
    logging.debug(
        f"Storage Details: Domain='{storage_domain_name}', Container='{storage_container_name}', Blob='{storage_blob_name_cleansed}'."
    )

    # Create credentials
    credential = get_azure_credential(
        managed_identity_client_id=managed_identity_client_id
    )

    # Create client
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_domain_name}", credential=credential
    )
    container_client = blob_service_client.get_container_client(
        container=storage_container_name
    )

    # Upload blob
    with open(file=file_path, mode="rb") as data:
        blob_client = await container_client.upload_blob(
            name=storage_blob_name_cleansed, data=data, overwrite=True
        )

    logging.info(f"Finished uploading file '{file_path}' to blob storage.")

    # Return blob url
    return blob_client.url


async def load_blob(
    storage_domain_name: str,
    storage_container_name: str,
    storage_blob_name: str,
    encoding: str = "utf-8",
    managed_identity_client_id: str = None,
) -> str:
    """Download file from blob storage async and return data.

    storage_domain_name (str): The domain name of the storage account.
    storage_container_name (str): The container name of the storage account.
    storage_blob_name (str): The blob name of the storage account.
    managed_identity_client_id (str): Specifies the managed identity client id used for auth.
    RETURNS (str): The data within the file.
    """
    logging.info(f"Start downloading file from blob storage.")

    # Preprocess storage blob name
    storage_blob_name_cleansed = unquote(storage_blob_name)
    logging.debug(
        f"Storage Details: Domain='{storage_domain_name}', Container='{storage_container_name}', Blob='{storage_blob_name_cleansed}'."
    )

    # Create credentials
    credential = get_azure_credential(
        managed_identity_client_id=managed_identity_client_id
    )

    # Create client
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_domain_name}", credential=credential
    )
    blob_client = blob_service_client.get_blob_client(
        container=storage_container_name, blob=storage_blob_name_cleansed
    )

    # Download blob
    download_stream = await blob_client.download_blob()
    data_bytes = await download_stream.readall()
    data = data_bytes.decode(encoding=encoding)

    logging.info(f"Finished downloading file from blob storage to memory.")

    # Return data
    return data


async def upload_string(
    data: str,
    storage_domain_name: str,
    storage_container_name: str,
    storage_blob_name: str,
    managed_identity_client_id: str = None,
) -> str:
    """Upload file to blob storage async from local storage.

    file_path (str): The file path to which the file will be downloaded.
    storage_domain_name (str): The domain name of the storage account.
    storage_container_name (str): The container name of the storage account.
    storage_blob_name (str): The blob name of the storage account.
    managed_identity_client_id (str): Specifies the managed identity client id used for auth.
    RETURNS (str): The url of the uploaded blob.
    """
    logging.info(f"Start uploading string to blob storage.")

    # Create credentials
    credential = get_azure_credential(
        managed_identity_client_id=managed_identity_client_id
    )

    # Create client
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_domain_name}", credential=credential
    )
    container_client = blob_service_client.get_container_client(
        container=storage_container_name
    )

    # Upload blob
    blob_client = await container_client.upload_blob(
        name=storage_blob_name, data=data, overwrite=True
    )

    logging.info(f"Finished uploading string to blob storage.")

    # Return blob url
    return blob_client.url


def delete_directory(directory_path: str) -> None:
    """Remove local directory recursively.

    directory_path (str): The directory path which will be removed.
    RETURNS (None): Returns no value.
    """
    logging.info(f"Start removing directory '{directory_path}' recursively.")

    # Check existence of directory and remove dir recursively
    if os.path.exists(path=directory_path):
        shutil.rmtree(path=directory_path, ignore_errors=True)
    else:
        logging.error(f"Provided directory path '{directory_path}' does not exist.")
        raise ValueError(f"Provided directory path '{directory_path}' does not exist.")

    logging.info(f"Finished removing directory '{directory_path}' recursively.")
