import logging

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General config
    PROJECT_NAME: str = "VideoAnalyzer"
    SERVER_NAME: str = "VideoAnalyzer"
    APP_VERSION: str = "v0.0.1"
    LOGGING_LEVEL: int = logging.INFO
    WEBSITE_NAME: str = Field(default="test", alias="WEBSITE_SITE_NAME")
    WEBSITE_INSTANCE_ID: str = Field(default="0", alias="WEBSITE_INSTANCE_ID")
    HOME_DIRECTORY: str = Field(default="", alias="HOME")
    MANAGED_IDENTITY_CLIENT_ID: str

    # Logging settings
    LOGGING_LEVEL: int = logging.DEBUG
    DEBUG: bool = True
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = Field(
        default="", alias="APPLICATIONINSIGHTS_CONNECTION_STRING"
    )

    # Azure AI Service config
    AZURE_AI_SERVICE_BASE_URL: str = "https://durable-aoai001.openai.azure.com/"
    AZURE_AI_SERVICE_API_VERSION: str = "2024-05-01-preview"

    # Azure AI Service config
    AZURE_AI_SPEECH_RESOURCE_ID: str
    AZURE_AI_SPEECH_BASE_URL: str
    AZURE_AI_SPEECH_API_VERSION: str = "2024-05-15-preview"
    AZURE_AI_SPEECH_PRIMARY_ACCESS_KEY: str

    # Azure Open AI config
    AZURE_OPEN_AI_BASE_URL: str = "https://durable-aoai001.openai.azure.com/"
    AZURE_OPEN_AI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPEN_AI_DEPLOYMENT_NAME: str = "gpt-4o"
    AZURE_OPEN_AI_TEMPERATURE: float = 0.0

    # Storage config
    STORAGE_DOMAIN_NAME: str = Field(
        default="rgdurablefunctiona8c3.blob.core.windows.net",
        alias="STORAGE_DOMAIN_NAME",
    )
    STORAGE_CONTAINER_UPLOAD_NAME: str = Field(
        default="upload-newsvideos",
        alias="STORAGE_CONTAINER_UPLOAD_NAME",
        min_length=3,
        max_length=63,
    )
    STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME: str = Field(
        default="internal-videos",
        alias="STORAGE_CONTAINER_INTERNAL_VIDEOS_NAME",
        min_length=3,
        max_length=63,
    )
    STORAGE_CONTAINER_INTERNAL_ANALYSIS_SPEECH_NAME: str = Field(
        default="internal-analysis-speech",
        alias="STORAGE_CONTAINER_INTERNAL_ANALYSIS_SPEECH_NAME",
        min_length=3,
        max_length=63,
    )
    STORAGE_CONTAINER_INTERNAL_ANALYSIS_VIDEO_NAME: str = Field(
        default="internal-analysis-video",
        alias="STORAGE_CONTAINER_INTERNAL_ANALYSIS_VIDEO_NAME",
        min_length=3,
        max_length=63,
    )
    STORAGE_CONTAINER_RESULTS_NAME: str = Field(
        default="results-newsvideos",
        alias="STORAGE_CONTAINER_RESULTS_NAME",
        min_length=3,
        max_length=63,
    )

    # News tag extraction config
    ROOT_FOLDER_NAME: str = "newstagextraction"
    SYSTEM_PROMPT: str = """
    You are a world class assistant for identifying news sections.
    Do the following with the provided news content and provide a valid JSON response that uses the schema mentioned below:
    1. Split the provided news content into broad thematic sections. The content of each section must cover a common news topic, whereas each section must comply with the following rules:
        a) The first sentence in the provided news content must be part of the first section. The last sentence in the provided news content must be part of the last section.
        b) Each section must start and end with a full sentence.
        c) Each section should consist of at least 3 sentences.
        d) Every sentences of the provided new content must be part of exactly one section. If you are unsure about one sentence, then assign it to the previous section.
        e) The last sentence of one section must by followed by the first sentence of the next section.
        f) The sections are not allowed to overlap and must be mutually exclusive.
        g) It is ok if some sections consist of 20 or more sentences and other sections only consist of 3 or more sentences.
    3. You must find the first sentence and last sentence of each section. Define the first sentence as start and the last sentence as end.
    4. Generate a title for each news section.
    5. Add one category to each section that matches the content. Assign one of the following categories: politics, sports, economy, environment, international, technology, health, meteorology, national, culture, justice, events.
    6. Add tags to each section. Samples for tags are: sports, weather, international news, national news, politics, crime, technology, celebrity, other. Add up to 5 additional tags based on the content of each section.
    7. Generate a score between 0 and 10 for each section. The score indicates how good the defined tags match the content of the section. 0 indicates that the tags don't match the content, and 10 means that the tags are a perfect match.
    8. Translate the title and tags for each section into the language of the news content.
    Here is a sample JSON response:
    {format_sample}
    """
    USER_PROMPT: str = """
    News Content: "{news_content}"
    ---
    Identify news sections for the provided news text according to the instructions. The text is from the following tv show: {news_show_details}
    """


settings = Settings()
