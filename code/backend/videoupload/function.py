import logging

import azure.functions as func
import azurefunctions.extensions.bindings.blob as blob

from shared.config import settings
from shared.utils import copy_blob, download_blob, get_guid, upload_blob
from videoupload.speech import SpeechClient
from videoupload.utils import extract_audio_from_video

import os


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
    download_file_path = os.path.join(
        settings.HOME_DIRECTORY, videoupload_guid, f"video.{blob_file_type}"
    )
    result_download_blob = await download_blob(
        file_path=download_file_path,
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        storage_container_name=client.container_name,
        storage_blob_name=client.blob_name,
    )
    logging.info(f"Downloaded blob to '{result_download_blob}'.")

    # Copy blob from upload location
    logging.info(f"Copy blob into destination container.")
    await copy_blob(
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        source_storage_container_name=client.container_name,
        source_storage_blob_name=client.blob_name,
        sink_storage_container_name=settings.STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME,
        sink_storage_blob_name=f"{videoupload_guid}/video.{blob_file_type}",
        delete_source=True,
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
    result_upload_blob = upload_blob(
        file_path=result_extract_audio_from_video,
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        storage_container_name=settings.STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME,
        storage_blob_name=f"{videoupload_guid}/{audio_file_name}",
    )

    # Create AI Speech STT batch job
    logging.info(f"Create AI Speech STT batch job.")
    speech_client = SpeechClient(
        azure_ai_speech_base_url=settings.AZURE_AI_SPEECH_BASE_URL,
        azure_ai_speech_api_version=settings.AZURE_AI_SPEECH_API_VERSION,
    )
    result_create_transcription_job = speech_client.create_transcription_job(
        guid=seed_guid,
        blob_url=result_upload_blob,
    )
