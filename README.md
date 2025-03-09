# SYNC Server LLM

## Installation

```shell
git clone --recurse-submodules https://github.com/NCTU-SYNC/sync-server-llm.git
cd sync-server-llm

uv run gen-protos
```

## Usage

Please configure the `configs/config.toml` file.
The following environment variables are required (`export` them or place them in a `.env` file):

- `OPENAI_API_KEY`: Your ChatGPT API key.
- `QDRANT_HOST`: The Qdrant host address.
- `QDRANT_PORT`: The Qdrant host port.
- `QDRANT_COLLECTION`: The Qdrant collection name.

```shell
python3 scripts/serve.py --config configs/config.toml
```

## Features

Refer to the protobuf files in the `protos/` directory for the features provided by the server.
