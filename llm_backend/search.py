from typing import Optional

import chromadb
import grpc
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from llm_backend.grpc import search_pb2
from llm_backend.grpc import search_pb2_grpc
from llm_backend.grpc.search_pb2_grpc import \
    add_SearchServiceServicer_to_server

__all__ = [
    'SearchService',
    'add_SearchServiceServicer_to_server',
]

DEFAULT_EMBEDDING_MODEL = 'sentence-transformers/distiluse-base-multilingual-cased-v1'
DEFAULT_SIMILARITY_TOP_K = 3
DEFAULT_SEARCH_QUERY_TEMPLATE = """
Please search for the content related to the following keywords: {keywords}.
"""


class SearchService(search_pb2_grpc.SearchServiceServicer):

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8000,
        collection: str = 'news',
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        query_template: Optional[str] = None,
        similarity_top_k: Optional[int] = None,
    ):
        """Initialize ChromaDBWriter.

        Args:
            host: Host of ChromaDB server. Set to 'test' for testing.
            port: Port of ChromaDB server.
            collection: Name of collection.
            embedding_model: Name of embedding model. All available
                models can be found [here](https://huggingface.co/models?language=zh)
            query_template: Template for search query.
            similarity_top_k: Number of top results to return.
        """
        if host == 'test':
            client = chromadb.PersistentClient()
        else:
            client = chromadb.HttpClient(host=host, port=port)

        vector_store = ChromaVectorStore(
            chroma_collection=client.get_or_create_collection(collection))
        embed_model = HuggingFaceEmbedding(model_name=embedding_model)

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, embed_model=embed_model)

        self.query_template = query_template or DEFAULT_SEARCH_QUERY_TEMPLATE
        self.similarity_top_k = similarity_top_k or DEFAULT_SIMILARITY_TOP_K

    def Search(
        self,
        request: search_pb2.SearchRequest,
        _context: grpc.ServicerContext,
    ):
        prompt = self.query_template.format(
            keywords=', '.join(request.keywords))
        similarity_top_k = request.similarity_top_k or self.similarity_top_k

        retriever = self.index.as_retriever(similarity_top_k=similarity_top_k)
        results = retriever.retrieve(prompt)

        return search_pb2.SearchResponse(
            ids=[result.node_id for result in results])
