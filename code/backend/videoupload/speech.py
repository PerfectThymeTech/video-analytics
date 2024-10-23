import logging
from typing import Dict

import httpx
from shared.utils import get_azure_credential


class SpeechClient:
    def __init__(
        self,
        azure_ai_speech_base_url: str,
        azure_ai_speech_api_version: str,
        azure_ai_speech_primary_access_key: str = None,
        managed_identity_client_id: str = None,
    ):
        """Initializes the speech client.

        azure_ai_speech_base_url (str): Specifies the base url of the ai speech service.
        azure_ai_speech_api_version (str): Specifies the api version used for the speech service.
        managed_identity_client_id (str): Specifies the managed identity client id used for auth.
        RETURNS (None): No return values.
        """
        self.azure_ai_speech_primary_access_key = azure_ai_speech_primary_access_key
        self.azure_ai_speech_base_url = azure_ai_speech_base_url
        self.azure_ai_speech_api_version = azure_ai_speech_api_version
        self.managed_identity_client_id = managed_identity_client_id

    async def create_transcription_job(self, guid: str, blob_url: str) -> str:
        """Creates a batch transcription job for a blob file.

        guid (str): Specifies the guid used as a name for the processing job.
        blob_url (str): Specifies the blob url pointing to an audio file that will be transcribed.
        RETURNS (str): Returns the transaction url of the transcription job.
        """
        # Define url
        url = f"{self.azure_ai_speech_base_url}/speechtotext/transcriptions:submit?api-version={self.azure_ai_speech_api_version}"

        # Get headers
        headers = self.__get_headers()

        # Define payload
        payload = {
            "displayName": f"{guid}",
            "description": "STT for video file",
            "contentUrls": [blob_url],
            "locale": "es-ES",
            "properties": {
                "languageIdentification": {
                    "mode": "Single",
                    "candidateLocales": ["en-US", "de-DE", "es-ES", "pt-PT", "fr-FR"],
                },
                "diarizationEnabled": False,
                "wordLevelTimestampsEnabled": False,
                "displayFormWordLevelTimestampsEnabled": False,
                "punctuationMode": "DictatedAndAutomatic",
                "profanityFilterMode": "None",
                "timeToLive": "PT12H",
            },
        }

        # Send request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                headers=headers,
                json=payload,
            )

        # Get transaction id
        transaction_id_url = response.json().get("self")
        transcription_id = str.split(transaction_id_url, sep="/")[
            -1
        ]  # transaction_id_url is None and copy fails
        logging.debug(f"Submitted transcription job with id '{transcription_id}'")

        return transcription_id

    async def get_transcription_job(self, transcription_id: str):
        pass

    async def __get_headers(self) -> Dict:
        """Creates the headers required for the azure ai service.

        RETURNS (Dict): Headers used for the API calls.
        """
        if self.azure_ai_speech_primary_access_key:
            # Create headers
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": self.azure_ai_speech_primary_access_key,
            }
        else:
            # Generate token
            credential = get_azure_credential(
                managed_identity_client_id=self.managed_identity_client_id,
            )
            token = await credential.get_token(
                "https://cognitiveservices.azure.com/.default"
            )

            # Create headers
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token.token}",
            }
        return headers
