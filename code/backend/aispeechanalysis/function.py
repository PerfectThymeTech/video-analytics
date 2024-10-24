import logging
import json

import azure.functions as func
import azurefunctions.extensions.bindings.blob as blob
from shared.utils import load_blob
from shared.config import settings
from aispeechanalysis.utils import get_transcript
from aispeechanalysis.llm import LlmClient


bp = func.Blueprint()


@bp.function_name("AiSpeechAnalysis")
@bp.blob_trigger(
    arg_name="client",
    path="internal-analysis-speech/{name}",
    connection="BlobTrigger",
    # source="LogsAndContainerScan",
)
async def ai_speech_analysis(client: blob.BlobClient) -> func.HttpResponse:
    logging.info(f"Azure AI Speech file upload detected.")

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
    result_get_transcript = get_transcript(
        ai_speech_blob_json=blob_json
    )

    # Use Open AI to generate scenes
    logging.info("Use Open AI to generate scenes")
    llm_client = LlmClient(
        azure_open_ai_base_url=settings.AZURE_OPEN_AI_BASE_URL,
        azure_open_ai_api_version=settings.AZURE_OPEN_AI_API_VERSION,
        azure_open_ai_deployment_name=settings.AZURE_OPEN_AI_DEPLOYMENT_NAME,
        azure_open_ai_temperature=settings.AZURE_OPEN_AI_TEMPERATURE,
    )
    result_invoke_llm_chain = llm_client.invoke_llm_chain(
        news_content=result_get_transcript,
        news_show_details="This is a news show covering different news content.",
        language=settings.MAIN_CONTENT_LANGUAGE
    )

    
