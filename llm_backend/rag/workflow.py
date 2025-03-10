import qdrant_client
from llama_index.core import ChatPromptTemplate, VectorStoreIndex
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import PromptType
from llama_index.core.response_synthesizers import (
    ResponseMode,
    get_response_synthesizer,
)
from llama_index.core.schema import NodeWithScore
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore

from .config import RagConfig, RetrieveConfig, SummarizeConfig
from .content_formatters import CONTENT_FORMATTERS


class RetrieveResult(BaseModel):
    news_id: str = Field(description="The mongodb id of the retrieved news.")
    score: float = Field(description="The score of the retrieved news.")
    content: str = Field(description="The content of the retrieved news.")


class RetrieveEvent(Event):
    results: list[RetrieveResult]


class RagWorkflow(Workflow):
    def __init__(self, config: RagConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_retrieve_service(config.retrieve)
        self.__init_summarize_service(config.summarize)

    def __init_retrieve_service(self, config: RetrieveConfig):
        if (host := config.vector_database.host) == "test":
            client = qdrant_client.AsyncQdrantClient(location=":memory:")
        else:
            client = qdrant_client.AsyncQdrantClient(
                host=host,
                port=config.vector_database.port,
            )

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=QdrantVectorStore(
                aclient=client,
                collection_name=config.vector_database.collection,
            ),
            embed_model=HuggingFaceEmbedding(
                model_name=config.embedding_model,
            ),
        )

        self.query_template = config.prompt_template
        self.similarity_top_k = config.similarity_top_k

    def __init_summarize_service(self, config: SummarizeConfig):
        self.summarizer = get_response_synthesizer(
            llm=OpenAI(model=config.llm.model, api_key=config.llm.api_key),
            response_mode=ResponseMode.SIMPLE_SUMMARIZE,
            use_async=True,
        )
        summarizer_prompt = ChatPromptTemplate(
            message_templates=[
                ChatMessage(role=MessageRole.SYSTEM, content=config.system_template),
                ChatMessage(role=MessageRole.USER, content=config.user_template),
            ],
            prompt_type=PromptType.SUMMARY,
        )
        self.summarizer.update_prompts({"text_qa_template": summarizer_prompt})

        self.query_str = config.query_str
        self.content_formatter = CONTENT_FORMATTERS[config.content_format]

    @step
    async def retrieve(self, ev: StartEvent) -> RetrieveEvent:
        prompt = self.query_template.format(keywords=", ".join(ev.keywords))
        similarity_top_k = ev.similarity_top_k or self.similarity_top_k

        retriever = self.index.as_retriever(similarity_top_k=similarity_top_k)
        retrieved_results: list[NodeWithScore] = await retriever.aretrieve(prompt)

        return RetrieveEvent(
            results=[
                RetrieveResult(
                    news_id=result.metadata["news_id"],
                    score=result.get_score(),
                    content="".join(result.text.split()),
                )
                for result in retrieved_results
            ]
        )

    @step
    async def summarize(self, ev: RetrieveEvent) -> StopEvent:
        contents = [result.content for result in ev.results]
        texts = self.content_formatter(contents)
        summary = str(await self.summarizer.aget_response(self.query_str, texts))
        return StopEvent(
            result={
                "retrieved_ids": [result.news_id for result in ev.results],
                "summary": summary,
            }
        )
