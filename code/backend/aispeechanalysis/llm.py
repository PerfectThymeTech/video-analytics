import logging

from aispeechanalysis.models import InvokeLlmResponse
from azure.identity import DefaultAzureCredential
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser  # , JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from shared.config import settings


class LlmMessages:
    SYSTEM_MESSAGE: str = settings.SYSTEM_PROMPT
    USER_MESSAGE: str = settings.USER_PROMPT


class LlmClient:
    def __init__(
        self,
        azure_open_ai_base_url: str,
        azure_open_ai_api_version: str,
        azure_open_ai_deployment_name: str,
        azure_open_ai_temperature: float,
        managed_identity_client_id: str = None,
    ) -> None:
        """Initializes the llm client.

        azure_open_ai_base_url (str): Specifies the base url of the azure open ai service.
        azure_open_ai_api_version (str): Specifies the api version used for the azure open ai service.
        azure_open_ai_deployment_name (str): Specifies the deployment name used within azure open ai service.
        azure_open_ai_temperature (float): Specifies the temparature used for the model.
        managed_identity_client_id (str): Specifies the managed identity client id used for auth.
        RETURNS (None): No return values.
        """
        # Create llm chain
        self.__create_llm_chain(
            azure_open_ai_base_url=azure_open_ai_base_url,
            azure_open_ai_api_version=azure_open_ai_api_version,
            azure_open_ai_deployment_name=azure_open_ai_deployment_name,
            azure_open_ai_temperature=azure_open_ai_temperature,
            managed_identity_client_id=managed_identity_client_id,
        )

    def __create_llm_chain(
        self,
        azure_open_ai_base_url: str,
        azure_open_ai_api_version: str,
        azure_open_ai_deployment_name: str,
        azure_open_ai_temperature: float,
        managed_identity_client_id: str,
    ) -> None:
        # Create chat prompt template
        logging.debug("Creating chat prompt template")
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=LlmMessages.SYSTEM_MESSAGE, type="system"),
                ("user", LlmMessages.USER_MESSAGE),
            ],
        )
        prompt.input_variables = [
            "format_instructions",
            "news_content",
            "language",
            "news_show_details",
        ]

        # Create the llm
        logging.debug("Creating the llm")

        def entra_id_token_provider():
            credential = DefaultAzureCredential(
                managed_identity_client_id=managed_identity_client_id,
            )
            token = credential.get_token(
                "https://cognitiveservices.azure.com/.default"
            ).token
            return token

        llm = AzureChatOpenAI(
            azure_endpoint=azure_open_ai_base_url,
            api_version=azure_open_ai_api_version,
            deployment_name=azure_open_ai_deployment_name,
            azure_ad_token_provider=entra_id_token_provider,
            temperature=azure_open_ai_temperature,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        # Create the output parser
        logging.debug("Creating the output parser")
        # output_parser = JsonOutputParser(pydantic_object=InvokeLlmResponse)
        output_parser = PydanticOutputParser(pydantic_object=InvokeLlmResponse)

        # Insert partial into prompt
        prompt_partial = prompt.partial(
            format_instructions=output_parser.get_format_instructions(),
        )
        logging.debug(f"Prompt: {prompt.model_dump_json()}")

        # Create llm chain with retry
        logging.debug("Creating the llm chain with retry")
        llm_chain = prompt_partial | llm | output_parser
        self.__llm_chain = llm_chain.with_retry()

    def invoke_llm_chain(
        self,
        news_content: str,
        news_show_details: str,
        language: str,
    ) -> InvokeLlmResponse:
        result: InvokeLlmResponse = self.__llm_chain.invoke(
            {
                "news_content": news_content,
                "news_show_details": news_show_details,
                "language": language,
            },
        )
        return result
