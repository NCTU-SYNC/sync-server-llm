import grpc
import qdrant_client
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

from llm_backend.protos import search_pb2, search_pb2_grpc
from llm_backend.protos.search_pb2_grpc import add_SearchServiceServicer_to_server

__all__ = [
    "SearchService",
    "add_SearchServiceServicer_to_server",
]

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v1"
DEFAULT_SIMILARITY_TOP_K = 3
DEFAULT_SEARCH_QUERY_TEMPLATE = """
Please search for the content related to the following keywords: {keywords}.
"""


class SearchService(search_pb2_grpc.SearchServiceServicer):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection: str = "news",
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        query_template: str | None = None,
        similarity_top_k: int | None = None,
    ):
        """
        Args:
            host: Host of QDrant server. Set to 'test' for testing.
            port: Port of QDrant server.
            collection: Name of collection.
            embedding_model: Name of embedding model. All available
                models can be found [here](https://huggingface.co/models?language=zh)
            query_template: Template for search query.
            similarity_top_k: Number of top results to return.
        """
        if host == "test":
            client = qdrant_client.AsyncQdrantClient(location=":memory:")
        else:
            client = qdrant_client.AsyncQdrantClient(
                host=host,
                port=port,
            )

        vector_store = QdrantVectorStore(
            aclient=client,
            collection_name=collection,
        )
        embed_model = HuggingFaceEmbedding(model_name=embedding_model)

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, embed_model=embed_model
        )

        self.query_template = query_template or DEFAULT_SEARCH_QUERY_TEMPLATE
        self.similarity_top_k = similarity_top_k or DEFAULT_SIMILARITY_TOP_K

    def Search(
        self,
        request: search_pb2.SearchRequest,
        _context: grpc.ServicerContext,
    ):
        prompt = self.query_template.format(keywords=", ".join(request.keywords))
        similarity_top_k = request.similarity_top_k or self.similarity_top_k

        retriever = self.index.as_retriever(similarity_top_k=similarity_top_k)
        results: list[NodeWithScore] = retriever.retrieve(prompt)

        return search_pb2.SearchResponse(
            results=[
                search_pb2.RetrieveResult(
                    id=result.node_id,
                    score=result.score,
                    content="".join(result.text.split()),
                )
                for result in results
            ]
        )
