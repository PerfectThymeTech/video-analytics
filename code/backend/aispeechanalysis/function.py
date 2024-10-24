import json
import logging

import azure.functions as func
import azurefunctions.extensions.bindings.blob as blob
from aispeechanalysis.llm import LlmClient
from aispeechanalysis.utils import get_transcript
from shared.config import settings
from shared.utils import load_blob, upload_string

bp = func.Blueprint()


@bp.function_name("AiSpeechAnalysis")
@bp.blob_trigger(
    arg_name="client",
    path="internal-analysis-speech/{name}",
    connection="BlobTrigger",
    # source="LogsAndContainerScan",
)
async def ai_speech_analysis(client: blob.BlobClient) -> func.HttpResponse:
    logging.info("Azure AI Speech file upload detected.")

    # Initialize
    logging.info("Initialize")
    ai_speech_analysis_guid = str.split(client.blob_name, sep="/")[0]

    # Download blob file content and convert to json
    logging.info("Download blob file content and convert to json.")
    result_load_blob = await load_blob(
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        storage_container_name=client.container_name,
        storage_blob_name=client.blob_name,
        encoding="utf-8",
        managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
    )
    blob_json = json.loads(result_load_blob)
    logging.debug(f"Loaded blob content as json: '{blob_json}'")

    # Get transcript
    logging.info("Get transcript from Azure AI Speech content.")
    result_get_transcript = get_transcript(ai_speech_blob_json=blob_json)

    # Use Open AI to generate scenes
    logging.info("Use Open AI to generate scenes")
    llm_client = LlmClient(
        azure_open_ai_base_url=settings.AZURE_OPEN_AI_BASE_URL,
        azure_open_ai_api_version=settings.AZURE_OPEN_AI_API_VERSION,
        azure_open_ai_deployment_name=settings.AZURE_OPEN_AI_DEPLOYMENT_NAME,
        azure_open_ai_temperature=settings.AZURE_OPEN_AI_TEMPERATURE,
        managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
    )
    result_invoke_llm_chain = llm_client.invoke_llm_chain(
        news_content=result_get_transcript,
        news_show_details="This is a news show covering different news content.",
        language=settings.MAIN_CONTENT_LANGUAGE,
    )

    # Get timestamps
    # TODO

    # Save results
    logging.info("Save results")
    _ = await upload_string(
        data=result_invoke_llm_chain,
        storage_domain_name=f"{client.account_name}.blob.core.windows.net",
        storage_container_name=settings.STORAGE_CONTAINER_RESULTS_NAME,
        storage_blob_name=f"{ai_speech_analysis_guid}/llm.json",
        managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
    )
    # TODO
