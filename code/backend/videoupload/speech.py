import logging
from typing import Dict, List

import httpx
from shared.utils import get_azure_credential


class SpeechClient:
    def __init__(
        self,
        azure_ai_speech_resource_id: str,
        azure_ai_speech_base_url: str,
        azure_ai_speech_api_version: str,
        azure_ai_speech_primary_access_key: str = None,
        managed_identity_client_id: str = None,
    ):
        """Initializes the speech client.

        azure_ai_speech_resource_id (str): Specifies the resource id of the azure ai search service.
        azure_ai_speech_base_url (str): Specifies the base url of the ai speech service.
        azure_ai_speech_api_version (str): Specifies the api version used for the speech service.
        managed_identity_client_id (str): Specifies the managed identity client id used for auth.
        RETURNS (None): No return values.
        """
        self.azure_ai_speech_resource_id = azure_ai_speech_resource_id
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
        headers = await self.__get_headers()

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

        # Check response
        if response.status_code >= 400:
            message = f"Failed to create batch transcription job (status code: '{response.status_code}'): '{response.text}'"
            logging.error(message)
            raise httpx.RequestError(message)
        else:
            logging.info(
                f"Created batch transcription job (status code: '{response.status_code}'): '{response.text}'"
            )

        # Get transaction id
        transaction_id_url = response.json().get("self")
        transcription_id = str.split(
            str.split(transaction_id_url, sep="/")[-1], sep="?"
        )[0]
        logging.debug(f"Submitted transcription job with id '{transcription_id}'")

        return transcription_id

    async def get_transcription_job_status(self, transcription_id: str) -> str:
        """Returns the transcription job status.

        transcription_id (str): Specifies the trancription job id.
        RETURNS (str): Returns the status of the transcription job.
        """
        # Define url
        url = f"{self.azure_ai_speech_base_url}/speechtotext/transcriptions/{transcription_id}?api-version={self.azure_ai_speech_api_version}"

        # Get headers
        headers = await self.__get_headers()

        # Send request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
                headers=headers,
            )

        # Check response
        if response.status_code >= 400:
            message = f"Failed to get batch transcription job '{transcription_id}' (status code: '{response.status_code}'): '{response.text}'"
            logging.error(
                message,
            )
            raise httpx.RequestError(
                message,
            )
        else:
            logging.info(
                f"Received batch transcription job (status code: '{response.status_code}'): '{response.text}'"
            )

        # Get status
        status = response.json().get("status", None)
        logging.debug(f"Status of transcription job '{transcription_id}': '{status}'")
        return status

    async def get_transcription_job_file_list(
        self, transcription_id: str
    ) -> List[str]:
        """Returns the transcription job file list.

        transcription_id (str): Specifies the trancription job id.
        RETURNS (List[str]): Returns the list of file urls of the transcription job.
        """
        # Define url
        sas_validity_in_seconds = 600
        url = f"{self.azure_ai_speech_base_url}/speechtotext/transcriptions/{transcription_id}/files?sasValidityInSeconds={sas_validity_in_seconds}&api-version={self.azure_ai_speech_api_version}"

        # Get headers
        headers = await self.__get_headers()

        # Send request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
                headers=headers,
            )

        # Check response
        if response.status_code >= 400:
            message = f"Failed to get files list of batch transcription job '{transcription_id}' (status code: '{response.status_code}'): '{response.text}'"
            logging.error(
                message,
            )
            raise httpx.RequestError(
                message,
            )
        else:
            logging.info(
                f"Received batch transcription job files list (status code: '{response.status_code}'): '{response.text}'"
            )

        # Get files list
        response_value = response.json().get("values", [])

        # Get transcription file list
        transcription_file_url_list = []
        for value in response_value:
            if value.get("kind", "") == "Transcription":
                transcription_file_url = value.get("links", {"contentUrl": ""}).get(
                    "contentUrl", None
                )
                if transcription_file_url:
                    transcription_file_url_list.append(transcription_file_url)

        return transcription_file_url_list

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
                "Authorization": f"Bearer aad#{self.azure_ai_speech_resource_id}#{token.token}",
            }
        return headers
