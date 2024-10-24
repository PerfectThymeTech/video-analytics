import asyncio
import logging
import os

import azure.functions as func
import azurefunctions.extensions.bindings.blob as blob
from shared.config import settings
from shared.utils import (
    copy_blob,
    copy_blob_from_url,
    delete_directory,
    download_blob,
    get_guid,
    upload_blob,
)
from videoupload.speech import SpeechClient
from videoupload.utils import extract_audio_from_video

bp = func.Blueprint()


@bp.function_name("VideoUpload")
@bp.blob_trigger(
    arg_name="client",
    path="upload-newsvideos/{name}",
    connection="BlobTrigger",
    # source="LogsAndContainerScan",
)
async def upload_video(client: blob.BlobClient):
    logging.info("Video upload detected.")

    # Initialize
    logging.info("Initialize")
    seed_guid = f"{client.account_name}-{client.container_name}-{client.blob_name}"
    videoupload_guid = get_guid(seed=seed_guid)
    blob_file_type = str.split(client.blob_name, ".")[-1]

    # Download blob to local storage async
    logging.info(f"Download video for preprocessing.")
    download_directory_path = os.path.join(settings.HOME_DIRECTORY, videoupload_guid)
    download_file_path = os.path.join(
        download_directory_path, f"video.{blob_file_type}"
    )
    result_download_blob = await download_blob(
        file_path=download_file_path,
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        storage_container_name=client.container_name,
        storage_blob_name=client.blob_name,
        managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
    )
    logging.info(f"Downloaded blob to '{result_download_blob}'.")

    # Copy blob from upload location
    logging.info(f"Copy blob into destination container.")
    _ = await copy_blob(
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        source_storage_container_name=client.container_name,
        source_storage_blob_name=client.blob_name,
        sink_storage_container_name=settings.STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME,
        sink_storage_blob_name=f"{videoupload_guid}/video.{blob_file_type}",
        delete_source=True,
        managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
    )

    # Extract audio from video
    logging.info(f"Extract audio from video.")
    audio_file_name = f"audio.wav"
    result_extract_audio_from_video = extract_audio_from_video(
        file_path=result_download_blob,
        audio_file_name=audio_file_name,
    )

    # Upload audio blob
    logging.info(f"Upload audio blob to storage.")
    result_upload_blob = await upload_blob(
        file_path=result_extract_audio_from_video,
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        storage_container_name=settings.STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME,
        storage_blob_name=f"{videoupload_guid}/{audio_file_name}",
        managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
    )

    # Cleanup local files
    logging.info(f"Cleanup local files.")
    delete_directory(directory_path=download_directory_path)

    # Create AI Speech STT batch job
    logging.info(f"Create AI Speech STT batch job.")
    speech_client = SpeechClient(
        azure_ai_speech_resource_id=settings.AZURE_AI_SPEECH_RESOURCE_ID,
        azure_ai_speech_base_url=settings.AZURE_AI_SPEECH_BASE_URL,
        azure_ai_speech_api_version=settings.AZURE_AI_SPEECH_API_VERSION,
        azure_ai_speech_primary_access_key=settings.AZURE_AI_SPEECH_PRIMARY_ACCESS_KEY,
        managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
    )
    result_create_transcription_job = await speech_client.create_transcription_job(
        guid=videoupload_guid,
        blob_url=result_upload_blob,
    )

    # Check AI Speech STT batch job
    logging.info(f"Check AI Speech STT batch job.")
    status = "Unknown"
    while status not in ["Succeeded", "Failed", None]:
        await asyncio.sleep(1)
        status = await speech_client.get_transcription_job_status(
            transcription_id=result_create_transcription_job,
        )
        logging.info(
            f"Current status for transaction id '{result_create_transcription_job}' is '{status}'."
        )

    # Check final status
    logging.info(
        f"Check final status of batch transcription job {result_create_transcription_job}"
    )
    if status != "Succeeded":
        message = f"Batch transcription job '{result_create_transcription_job}' failed."
        logging.error(message)
        raise Exception(message)

    # Get batch transcription file list
    logging.info("Get batch transcription file list.")
    result_get_transcription_job_file_list = (
        await speech_client.get_transcription_job_file_list(
            transcription_id=result_create_transcription_job
        )
    )

    # Upload files to storage
    logging.info("Upload files to storage")
    for index, item in enumerate(result_get_transcription_job_file_list):
        _ = copy_blob_from_url(
            source_url=item,
            sink_storage_domain_name=f"{client.account_name}.blob.core.windows.net",
            sink_storage_container_name=settings.STORAGE_CONTAINER_INTERNAL_ANALYSIS_SPEECH_NAME,
            sink_storage_blob_name=f"{videoupload_guid}/speech{index}.json",
        )

    logging.info(f"Completed Function run '{videoupload_guid}' successfully.")
