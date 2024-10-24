from typing import List

from pydantic import AliasChoices, BaseModel, Field


class LlmResponseItem(BaseModel):
    id: int = Field(description="id of the subsection")
    title: str = Field(description="title of the subsection")
    category: str = Field(description="category of the subsection")
    tags: List[str] = Field(description="tags of the subsection")
    score: int = Field(description="score of the subsection")
    start: str = Field(
        description="start of the text of the subsection",
        validation_alias=AliasChoices("start", "start_sentence"),
    )
    end: str = Field(
        description="end of the text of the subsection",
        validation_alias=AliasChoices("end", "end_sentence"),
    )

    def get_item_text(self, start: bool = True) -> str:
        if start:
            return self.start
        else:
            return self.end


class InvokeLlmResponse(BaseModel):
    sections: List[LlmResponseItem] = Field(
        description="list of items describing the subsections",
        validation_alias=AliasChoices("sections", "news_sections", "root"),
    )

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    @staticmethod
    def to_json(obj) -> str:
        return obj.model_dump_json()

    @staticmethod
    def from_json(data: str):
        return InvokeLlmResponse.model_validate_json(data)
