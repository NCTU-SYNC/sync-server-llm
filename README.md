# SYNC Server LLM

## Overview

SYNC Server LLM is a gRPC-based server that performs document retrieval and summarization. It leverages Qdrant for vector search and OpenAI models to generate summaries of retrieved content based on user-provided keywords.

## Installation

```shell
git clone --recurse-submodules https://github.com/NCTU-SYNC/sync-server-llm.git
cd sync-server-llm

uv sync --no-dev --frozen

uv run gen-protos
```

## Usage

This section explains how to run the SYNC Server LLM using different methods.

1. Configure the server by editing `configs/config.toml`

2. Set up the required environment variables by adding them to a `.env` file

   | Variable            | Description                   |
   | ------------------- | ----------------------------- |
   | `OPENAI_API_KEY`    | Your ChatGPT API key          |
   | `QDRANT_HOST`       | The Qdrant host address       |
   | `QDRANT_PORT`       | The Qdrant host REST API port |
   | `QDRANT_COLLECTION` | The Qdrant collection name    |

3. Start the server:

   - To run the server locally:

      ```shell
      uv run scripts/serve.py --config configs/config.toml
      ```

   - To run the server using Docker:

      Build the Docker image:

      ```shell
      docker build -t sync/backend-llm .
      ```

      Run the container:

      ```shell
      docker run -p 50051:50051 \
            --env-file .env \
            -v $(pwd)/path/to/configs:/app/configs/config.toml \
            -v $(pwd)/path/to/hf_cache:/tmp/llama_index \
            sync/backend-llm
      ```

      > 1. If you are using Windows, you can add `--gpus=all` to the `docker run` command. Ensure that your Docker installation supports GPU usage.
      > 2. It is strongly recommended to mount the `hf_cache` directory to a persistent volume to avoid re-downloading the Hugging Face models every time the container is started.

## Client Example

You can refer to `scripts/client.py` for an example implementation of a client:

```shell
uv run scripts/client.py
```

## Features

Refer to the protobuf files in the `protos/` directory for the features provided by the server.
