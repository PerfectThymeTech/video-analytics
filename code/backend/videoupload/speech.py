import httpx
import logging
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials import AccessToken

class SpeechClient:
    def __init__(
        self,
        azure_speech_base_url: str,
        azure_speech_api_version: str,
    ):
        """Initializes the speech client.

        azure_speech_base_url (str): Specifies the base url of the ai speech service.
        azure_speech_api_version (str): Specifies the api version used for the speech service.
        RETURNS (None): No return values.
        """
        self.azure_speech_base_url = azure_speech_base_url
        self.azure_speech_api_version = azure_speech_api_version
    
    async def create_transcription_job(self, guid: str, blob_url: str) -> str:
        """Creates a batch transcription job for a blob file.

        guid (str): Specifies the guid used as a name for the processing job.
        blob_url (str): Specifies the blob url pointing to an audio file that will be transcribed.
        RETURNS (str): Returns the transaction url of the transcription job.
        """
        # Get token
        token = await self.__get_auth_token()

        # Define url
        url = f"{self.azure_speech_base_url}/speechtotext/transcriptions:submit?api-version={self.azure_speech_api_version}"
        
        # Define headers
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.token}"
        }

        # Define payload
        payload = {
            "displayName": f"{guid}",
            "description": "STT for video file",
            "contentUrls": [
                blob_url
            ],
            "locale": "es-ES",
            "properties": {
                "languageIdentification": {
                    "mode": "Single",
                    "candidateLocales": ["en-US", "de-DE", "es-ES", "pt-PT", "fr-FR"]
                },
                "diarizationEnabled": False,
                "wordLevelTimestampsEnabled": False,
                "displayFormWordLevelTimestampsEnabled": False,
                "punctuationMode": "DictatedAndAutomatic",
                "profanityFilterMode": "None",
                "timeToLive": "PT12H"
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
        transcription_id = str.split(transaction_id_url, sep="/")[-1]
        logging.debug(f"Submitted transcription job with id '{transcription_id}'")
        
        return transcription_id

    async def get_transcription_job(self, transcription_id: str):
        pass

    async def __get_auth_token(self) -> AccessToken:
        """Creates an entra id token for an azure ai service.

        RETURNS (AccessToken): Returns the access token object.
        """
        # Generate token
        credential = DefaultAzureCredential(
            managed_identity_client_id=self.managed_identity_client_id,
        )
        token = await credential.get_token("https://cognitiveservices.azure.com/.default")
        return token
