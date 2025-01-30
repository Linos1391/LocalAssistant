**Notice:** After [Quick Start](quick_start.md), all these models below are all installed. You should NOT download them again.

## Text Generation Model

### Overview

Text generation is the main model used for communicating between user and LocalAssistant. Got labeled as 'Text_Generation' or '1'.

### Downloading

I recommend to try Qwen, no need for `hf_token` and is light-weight.

```
locas.cmd download -n qwen Qwen/Qwen2.5-1.5B-Instruct 1
```

*(Choose other models from [here](https://huggingface.co/models?pipeline_tag=text-generation&library=safetensors&sort=trending).)*

If you're too familiar with HuggingFace and confident enough about your device, try '[meta-llama/Meta-Llama-3-8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B/tree/main)'.

## Sentence Transformer Model

### Overview

Sentence transformer is a model used to semantic search data from provided documents. Required for `locas docs ...`. Got labeled as 'Sentence_Transformer' or '2'.

### Downloading

What this model does is encoding docs and retrieving information. You will NOT need any *fancy and advance* models like MsMarco.

```
locas.cmd download -n minilm sentence-transformers/all-MiniLM-L6-v2 2
```

*(Choose other models from [here](https://huggingface.co/sentence-transformers?sort_models=modified#models).)*

## Cross Encoder Model

### Overview

Cross encoder is a model used to rerank data after retrieving information process. Required for `locas docs ...`. Got labeled as 'Cross_Encoder' or '3'.

### Download

```
locas.cmd download -n msmarco cross-encoder/ms-marco-MiniLM-L-6-v2 3
```

*(Choose other models from [here](https://huggingface.co/cross-encoder?sort_models=modified#models).)*

## Built-in Model

### Overview

Models here is NOT trained by me, but rather being used for LocalAssistant's function. If one is broken by any chances, try remove its folder in `models/built-in` and run installation again.

### Rebel - Relation Extraction

**Source:** [Babelscape/rebel-large](https://huggingface.co/Babelscape/rebel-large).

This model is used for relation extraction and creating knowledge graph. Required for memory function in `locas start` and relation extraction in `locas docs extract`.