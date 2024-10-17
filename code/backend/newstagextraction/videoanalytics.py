import httpx

from azure.identity import DefaultAzureCredential
from datetime import datetime
from models.videoanalytics import VideoAnalyticsPayload
from logging_utils import get_logger

logger = get_logger(__name__)


class VideoAnalytics:
    def __init__(self, azure_ai_service_base_url: str,
        azure_ai_service_api_version: str,
        azure_open_ai_base_url: str,
        azure_open_ai_deployment_name: str,
        managed_identity_client_id: str,
    ) -> None:
        self.azure_ai_service_base_url = azure_ai_service_base_url
        self.azure_ai_service_api_version = azure_ai_service_api_version
        self.managed_identity_client_id = managed_identity_client_id
        self.azure_open_ai_base_url = azure_open_ai_base_url
        self.azure_open_ai_deployment_name = azure_open_ai_deployment_name

    async def create_video_task(self, input_blob_url: str, output_container_url: str) -> str:
        # Generate token
        token = self.__get_auth_token()

        # Define headers
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.token}"
        }

        # Define data
        payload = VideoAnalyticsPayload()
        payload.input.url = input_blob_url
        payload.output.url = output_container_url
        payload.resource.completion.endpoint = f"{self.azure_open_ai_base_url}/openai/deployments/{self.azure_open_ai_deployment_name}/chat/completions"
        
        # Define task name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        task_name = f"news-analysis-{timestamp}"

        # request
        async with httpx.AsyncClient() as client:
            _ = await client.put(
                url=f"{self.azure_ai_service_base_url}/computervision/videoanalysis/videodescriptions/{task_name}?api-version={self.azure_ai_service_api_version}",
                headers=headers,
                data=payload.model_dump_json(),
            )
        
        return task_name

    async def get_video_task(self, task_name: str) -> str:
        # Generate token
        token = self.__get_auth_token()

        # Define headers
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.token}"
        }

        # request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self.azure_ai_service_base_url}/computervision/videoanalysis/videodescriptions/{task_name}?api-version={self.azure_ai_service_api_version}",
                headers=headers,
            )
        return response.data


    def __get_auth_token(self) -> str:
        # Generate token
        credential = DefaultAzureCredential(
            managed_identity_client_id=self.managed_identity_client_id,
        )
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        return token
