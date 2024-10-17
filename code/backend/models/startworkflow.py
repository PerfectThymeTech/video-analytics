from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class OrchestratorWorkflowEnum(str, Enum):
    NEWSTAGEXTRACTION = "newstag_extraction_orchestrator"


class StartWorkflowRequest(BaseModel):
    orchestrator_workflow_name: OrchestratorWorkflowEnum = Field(
        default=OrchestratorWorkflowEnum.NEWSTAGEXTRACTION,
        alias="orchestrator_workflow_name",
    )
    orchestrator_workflow_properties: Dict[str, Any] | None = Field(
        default=None, alias="orchestrator_workflow_properties"
    )
