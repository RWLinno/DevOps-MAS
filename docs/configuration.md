# DevOps-MAS Configuration Guide

This document provides detailed information about DevOps-MAS system configuration options to help you customize system behavior according to your needs.

## Configuration File Overview

DevOps-MAS uses a JSON format configuration file `config.json`. You can copy from `config.example.json` and modify as needed. The configuration file contains multiple sections controlling different aspects of the system.

## Configuration Options Details

### API Keys

```json
"api_keys": {
  "openai": "your_openai_api_key",
  "azure_openai": {
    "api_key": "your_azure_openai_api_key",
    "api_base": "https://your-resource-name.openai.azure.com",
    "api_version": "2023-05-15"
  },
  "anthropic": "your_anthropic_api_key"
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `openai` | String | OpenAI API key for accessing GPT models |
| `azure_openai.api_key` | String | Azure OpenAI service API key |
| `azure_openai.api_base` | String | Azure OpenAI service base URL |
| `azure_openai.api_version` | String | Azure OpenAI API version |
| `anthropic` | String | Anthropic API key for accessing Claude models |

### Directory Settings

```json
"directories": {
  "data_dir": "data",
  "cache_dir": "cache",
  "logs_dir": "logs"
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data_dir` | String | Directory for storing knowledge base and other data |
| `cache_dir` | String | Storage directory for model cache and temporary files |
| `logs_dir` | String | Storage directory for log files |

### Model Configuration

```json
"models": {
  "default_llm": "gpt-4-turbo",
  "embedding_model": "sentence-transformers/all-mpnet-base-v2",
  "fallback_llm": "gpt-3.5-turbo",
  "local_models": {
    "enabled": false,
    "path": "local_models",
    "model_name": "mistral-7b-instruct"
  }
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `default_llm` | String | Default large language model to use |
| `embedding_model` | String | Model for text embeddings |
| `fallback_llm` | String | Backup model when default model is unavailable |
| `local_models.enabled` | Boolean | Whether to enable local models |
| `local_models.path` | String | Storage path for local model files |
| `local_models.model_name` | String | Name of the local model |

### RAG Settings

```json
"rag": {
  "retrieval": {
    "top_k": 5,
    "similarity_threshold": 0.75,
    "chunk_size": 1000,
    "chunk_overlap": 200
  },
  "knowledge_base": {
    "default_index": "engineering_docs",
    "vector_store": "faiss",
    "update_frequency": "daily"
  }
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `retrieval.top_k` | Integer | Number of most relevant documents to return during retrieval |
| `retrieval.similarity_threshold` | Float | Minimum threshold for document relevance |
| `retrieval.chunk_size` | Integer | Document chunk size (number of characters) |
| `retrieval.chunk_overlap` | Integer | Number of overlapping characters between adjacent chunks |
| `knowledge_base.default_index` | String | Default knowledge base index name |
| `knowledge_base.vector_store` | String | Vector storage backend (faiss/milvus etc.) |
| `knowledge_base.update_frequency` | String | Knowledge base update frequency |

### Privacy Settings

```json
"privacy": {
  "mask_emails": true,
  "mask_phone_numbers": true,
  "mask_ips": true,
  "mask_urls": true,
  "mask_tokens": true,
  "mask_credit_cards": true,
  "allowed_domains": ["example.com", "example.org"],
  "hash_pii": true
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `mask_emails` | Boolean | Whether to mask email addresses |
| `mask_phone_numbers` | Boolean | Whether to mask phone numbers |
| `mask_ips` | Boolean | Whether to mask IP addresses |
| `mask_urls` | Boolean | Whether to mask URLs |
| `mask_tokens` | Boolean | Whether to mask sensitive tokens |
| `mask_credit_cards` | Boolean | Whether to mask credit card numbers |
| `allowed_domains` | String Array | List of domains not to be masked |
| `hash_pii` | Boolean | Whether to hash PII information |

### Logging Settings

```json
"logging": {
  "level": "INFO",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "to_file": true,
  "max_file_size_mb": 10,
  "backup_count": 5
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | String | Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `format` | String | Log message format |
| `to_file` | Boolean | Whether to write logs to file |
| `max_file_size_mb` | Integer | Maximum size of single log file (MB) |
| `backup_count` | Integer | Number of old log files to retain |

### API Service Settings

```json
"api_service": {
  "host": "0.0.0.0",
  "port": 8000,
  "workers": 4,
  "cors": {
    "allow_origins": ["*"],
    "allow_methods": ["*"],
    "allow_headers": ["*"]
  },
  "rate_limit": {
    "enabled": true,
    "rate": 100,
    "per_seconds": 60
  }
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | String | Host address for API service to listen on |
| `port` | Integer | Port for API service to listen on |
| `workers` | Integer | Number of server worker processes |
| `cors.allow_origins` | String Array | Allowed cross-origin sources |
| `cors.allow_methods` | String Array | Allowed HTTP methods |
| `cors.allow_headers` | String Array | Allowed HTTP headers |
| `rate_limit.enabled` | Boolean | Whether to enable rate limiting |
| `rate_limit.rate` | Integer | Maximum number of requests in time period |
| `rate_limit.per_seconds` | Integer | Time period for rate limiting (seconds) |

### Web Application Settings

```json
"web_app": {
  "port": 8501,
  "theme": {
    "primary_color": "#FF5733",
    "background_color": "#FFFFFF",
    "text_color": "#333333"
  },
  "page_title": "DevOps-MAS Intelligent Engineering Q&A System",
  "favicon": "assets/favicon.ico"
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `port` | Integer | Port for web application to listen on |
| `theme.primary_color` | String | Theme primary color (hexadecimal) |
| `theme.background_color` | String | Background color (hexadecimal) |
| `theme.text_color` | String | Text color (hexadecimal) |
| `page_title` | String | Web page title |
| `favicon` | String | Path to website icon |

### Caching Settings

```json
"caching": {
  "enabled": true,
  "ttl_seconds": 86400,
  "max_size_mb": 1024,
  "redis": {
    "enabled": false,
    "host": "localhost",
    "port": 6379,
    "password": "",
    "db": 0
  }
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `enabled` | Boolean | Whether to enable caching |
| `ttl_seconds` | Integer | Time to live for cache entries (seconds) |
| `max_size_mb` | Integer | Maximum size of local cache (MB) |
| `redis.enabled` | Boolean | Whether to use Redis cache |
| `redis.host` | String | Redis server hostname |
| `redis.port` | Integer | Redis server port |
| `redis.password` | String | Redis server password |
| `redis.db` | Integer | Redis database number to use |

### Advanced Options

```json
"advanced": {
  "max_tokens_per_request": 4096,
  "temperature": 0.7,
  "request_timeout": 60,
  "max_retries": 3,
  "retry_delay": 2,
  "session_expiry_hours": 24,
  "system_prompts": {
    "default": "You are DevOps-MAS, a professional engineering assistant skilled at solving technical problems.",
    "code_analysis": "You are a code analysis expert, please analyze the following code in detail...",
    "error_diagnosis": "You are an error diagnosis expert, please analyze the following error logs..."
  }
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_tokens_per_request` | Integer | Maximum number of tokens generated by model |
| `temperature` | Float | Model response randomness (0-1) |
| `request_timeout` | Integer | API request timeout (seconds) |
| `max_retries` | Integer | Maximum number of retries on request failure |
| `retry_delay` | Integer | Delay between retries (seconds) |
| `session_expiry_hours` | Integer | User session expiry time (hours) |
| `system_prompts.default` | String | Default system prompt |
| `system_prompts.code_analysis` | String | System prompt for code analysis scenarios |
| `system_prompts.error_diagnosis` | String | System prompt for error diagnosis scenarios |

## Environment Variable Override

You can also use environment variables to override settings in the configuration file. Environment variables take precedence over configuration file settings.

Environment variable names should follow the format: `DEVOPS_MAS_SECTION_PARAM`, for example:

- `DEVOPS_MAS_API_KEYS_OPENAI` - Override OpenAI API key
- `DEVOPS_MAS_LOGGING_LEVEL` - Override log level
- `DEVOPS_MAS_API_SERVICE_PORT` - Override API service port

## Configuration File Example

See [config.example.json](../config.example.json) for a complete configuration file example.

## Configuration File Validation

On startup, DevOps-MAS validates the configuration file. If configuration errors exist, the system will output detailed error messages and use default values in some cases.

You can validate the configuration file using the following command:

```bash
python -m src.utils.config_loader --validate
```

## Common Issues

### Configuration File Not Found

If the system reports that the configuration file cannot be found, ensure you have copied `config.example.json` to `config.json` and placed it in the correct location.

### API Key Issues

If API calls fail, check that your API keys are correctly set and have sufficient permissions and quota.

### Local Model Configuration

When using local models, ensure:
1. `models.local_models.enabled` is set to `true`
2. `models.local_models.path` points to a valid model directory
3. Your system has sufficient memory to load the specified model