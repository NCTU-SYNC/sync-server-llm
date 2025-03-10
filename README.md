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

## Configuration

Before running the server, you need to:

1. Configure the server settings in `configs/config.toml`

2. Create a `.env` file with the following environment variables:

   | Variable            | Description                   |
   | ------------------- | ----------------------------- |
   | `OPENAI_API_KEY`    | Your ChatGPT API key          |
   | `QDRANT_HOST`       | The Qdrant host address       |
   | `QDRANT_PORT`       | The Qdrant host REST API port |
   | `QDRANT_COLLECTION` | The Qdrant collection name    |

## Running the Server

You can run SYNC Server LLM using one of the following methods:

### Method 1: Running Locally

```shell
uv run scripts/serve.py --config configs/config.toml
```

### Method 2: Using Docker

1. Build the Docker image:

   ```shell
   docker build -t sync/backend-llm .
   ```

2. Run the container:

   ```shell
   docker run -p 50051:50051 \
         --env-file .env \
         -v $(pwd)/path/to/configs:/app/configs/config.toml \
         -v $(pwd)/path/to/hf_cache:/tmp/llama_index \
         sync/backend-llm
   ```

   > Notes:
   > - For Windows users, add `--gpus=all` to use GPU capabilities (requires Docker with GPU support)
   > - We strongly recommend mounting the `hf_cache` directory to avoid re-downloading Hugging Face models on container restart
   > - Make sure to [set up and run the Qdrant server](https://qdrant.tech/documentation/guides/installation/#docker-and-docker-compose) before starting

### Method 3: Using Docker Compose

A `docker-compose.yaml` file is included in the repository to simplify deployment with both the server and Qdrant database.

1. Build the services:

   ```shell
   docker-compose build
   ```

2. Start the services:

   ```shell
   docker-compose up -d
   ```

## Client Example

To test the server, you can use the provided client example:

```shell
uv run scripts/client.py
```

## Features

Refer to the protobuf files in the `protos/` directory for the features provided by the server.
