from typing import List

from pydantic import BaseModel


class Authentication(BaseModel):
    kind: str = "managedIdentity"

class Completion(BaseModel):
    kind: str = "gptv"
    endpoint: str
    authentication: Authentication

class Resource(BaseModel):
    completion: Completion

class Input(BaseModel):
    kind: str = "azureBlobFile"
    url: str
    domain: str = "Default"

class Output(BaseModel):
    kind: str = "azureBlobContainer"
    url: str
    authentication: Authentication

class Property(BaseModel):
    kind: str = "describe"
    description: str
    examples: List[str]

class VideoAnalyticsPayload(BaseModel):
    input: Input
    output: Output
    resource: Resource
    properties: object = {}
