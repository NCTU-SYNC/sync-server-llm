import grpc

from llm_backend.protos import rag_pb2, rag_pb2_grpc


def run_search():
    with grpc.insecure_channel(ADDRESS) as channel:
        client = rag_pb2_grpc.RagServiceStub(channel)

        request = rag_pb2.RagRequest(
            keywords=["台灣", "選舉"],
            similarity_top_k=5,
        )

        response = client.Rag(request)

        print(response)


if __name__ == "__main__":
    ADDRESS = "localhost:50051"
    print("Running search...")
    run_search()
