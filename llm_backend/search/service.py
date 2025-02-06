import grpc
import qdrant_client
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

from llm_backend.protos import search_pb2, search_pb2_grpc

from .config import SearchConfig


class SearchService(search_pb2_grpc.SearchServiceServicer):
    def __init__(
        self,
        config: SearchConfig,
    ):
        if (host := config.qdrant.host) == "test":
            client = qdrant_client.AsyncQdrantClient(location=":memory:")
        else:
            client = qdrant_client.AsyncQdrantClient(
                host=host,
                port=config.qdrant.port,
            )

        vector_store = QdrantVectorStore(
            aclient=client,
            collection_name=config.qdrant.collection,
        )
        embed_model = HuggingFaceEmbedding(model_name=config.embeddings.model)

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, embed_model=embed_model
        )

        self.query_template = config.query.prompt_template
        self.similarity_top_k = config.query.similarity_top_k

    def Search(
        self,
        request: search_pb2.SearchRequest,
        context: grpc.ServicerContext,
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
