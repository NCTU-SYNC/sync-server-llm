import grpc

from llm_backend.protos import rag_pb2, rag_pb2_grpc
from llm_backend.rag.config import RagConfig
from llm_backend.rag.workflow import RagWorkflow


class RagService(rag_pb2_grpc.RagServiceServicer):
    def __init__(self, config: RagConfig):
        self.workflow = RagWorkflow(config=config)

    async def Rag(
        self,
        request: rag_pb2.RagRequest,
        context: grpc.aio.ServicerContext,
    ):
        result = await self.workflow.run(
            keywords=request.keywords,
            similarity_top_k=request.similarity_top_k,
        )

        return rag_pb2.RagResponse(
            retrieved_ids=result["retrieved_ids"],
            summary=result["summary"],
        )
