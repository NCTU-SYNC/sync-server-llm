from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..utils import contains_placeholder

DEFAULT_EMBEDDING_MODEL = "moka-ai/m3e-base"
DEFAULT_SIMILARITY_TOP_K = 3
DEFAULT_QUERY_PROMPT_TEMPLATE = (
    "Please search for the content related to the following keywords: {keywords}."
)


class QDrantConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        env_prefix="QDRANT_",
        case_sensitive=True,
        extra="ignore",
    )

    host: str = Field("test", validation_alias="HOST")
    port: int = Field(
        6333,  # 6333 is the default port of Qdrant
        validation_alias="PORT",
        gt=0,
    )
    collection: str = Field("news", validation_alias="COLLECTION")


class EmbeddingsConfig(BaseModel):
    model: str = Field(
        DEFAULT_EMBEDDING_MODEL,
        description="Name of embedding model. "
        "All available models can be found [here](https://huggingface.co/models?library=sentence-transformers&language=zh).",
    )


class QueryConfig(BaseModel):
    prompt_template: Annotated[
        str, AfterValidator(contains_placeholder("keywords"))
    ] = DEFAULT_QUERY_PROMPT_TEMPLATE
    similarity_top_k: int = Field(DEFAULT_SIMILARITY_TOP_K, gt=0)


class SearchConfig(BaseModel):
    qdrant: QDrantConfig = Field(default_factory=QDrantConfig)  # type: ignore
    embeddings: EmbeddingsConfig
    query: QueryConfig
