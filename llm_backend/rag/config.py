from typing import Annotated

from llama_index.llms.openai.utils import ALL_AVAILABLE_MODELS
from pydantic import AfterValidator, BaseModel, Field
from pydantic_settings import BaseSettings

from .content_formatters import ContentFormat

DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_SIMILARITY_TOP_K = 10
DEFAULT_QUERY_PROMPT_TEMPLATE = (
    "Please search for the content related to the following keywords: {keywords}."
)
DEFAULT_SYSTEM_TEMPLATE = (
    "You are an expert Q&A system that is trusted around the world.\n"
    "Always answer the query using the provided context information,"
    "and not prior knowledge.\n"
    "Some rules to follow:\n"
    "1. Never directly reference the given context in your answer.\n"
    "2. Avoid statements like 'Based on the context, ...' or"
    "The context information ...' or anything along"
    "those lines."
)
DEFAULT_USER_TEMPLATE = (
    "Context information from multiple sources is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the information from multiple sources and not prior knowledge,"
    "answer the query.\n"
    "Query: {query_str}\n"
    "Answer:"
)
DEFAULT_QUERY_STR = "請用繁體中文總結這幾篇新聞。"


def contains_placeholder(*placeholders: str):
    def validate_template(template: str):
        for placeholder in placeholders:
            if f"{{{placeholder}}}" not in template:
                raise ValueError(f"Template must contain '{{{placeholder}}}'")
        return template

    return validate_template


class QDrantConfig(BaseSettings):
    host: str = Field("test", validation_alias="QDRANT_HOST")
    port: int = Field(6333, gt=0, validation_alias="QDRANT_PORT")
    collection: str = Field("news", validation_alias="QDRANT_COLLECTION")


class RetrieveConfig(BaseModel):
    vector_database: QDrantConfig = QDrantConfig()  # type: ignore
    embedding_model: str = Field(
        DEFAULT_EMBEDDING_MODEL,
        description="Name of embedding model."
        "All available models can be found [here](https://huggingface.co/models?library=sentence-transformers&language=zh).",
    )
    prompt_template: Annotated[
        str, AfterValidator(contains_placeholder("keywords"))
    ] = DEFAULT_QUERY_PROMPT_TEMPLATE
    similarity_top_k: int = Field(DEFAULT_SIMILARITY_TOP_K, gt=1)


def is_available_model(model_name: str):
    if model_name not in ALL_AVAILABLE_MODELS:
        raise ValueError(
            f"Model {model_name} is not available. Available models are: {ALL_AVAILABLE_MODELS}"
        )
    return model_name


class ChatGptConfig(BaseSettings):
    api_key: str = Field(validation_alias="OPENAI_API_KEY")
    model: Annotated[
        str,
        Field(DEFAULT_OPENAI_MODEL),
        AfterValidator(is_available_model),
    ]


class SummarizeConfig(BaseModel):
    llm: ChatGptConfig = ChatGptConfig()  # type: ignore
    system_template: str = DEFAULT_SYSTEM_TEMPLATE
    user_template: Annotated[
        str, AfterValidator(contains_placeholder("context_str", "query_str"))
    ] = DEFAULT_USER_TEMPLATE
    query_str: str = Field(
        DEFAULT_QUERY_STR,
        description="The content of `{query_str}` placeholder in the user template.",
    )
    content_format: ContentFormat = ContentFormat.PLAIN


class RagConfig(BaseModel):
    retrieve: RetrieveConfig
    summarize: SummarizeConfig
