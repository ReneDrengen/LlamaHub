"""Init file of LlamaIndex."""
from pathlib import Path

with open(Path(__file__).absolute().parents[0] / "VERSION") as _f:
    __version__ = _f.read().strip()


import logging
from logging import NullHandler
from typing import Callable, Optional

# import global eval handler
from llama_index.callbacks.global_handlers import set_global_handler
from llama_index.data_structs.struct_type import IndexStructType

# embeddings
from llama_index.embeddings.openai import OpenAIEmbedding

# structured
from llama_index.indices.common.struct_store.base import SQLDocumentContextBuilder

# for composability
from llama_index.indices.composability.graph import ComposableGraph

# indices
from llama_index.indices.list import ListIndex, SummaryIndex

# loading
from llama_index.indices.loading import (
    load_graph_from_storage,
    load_index_from_storage,
    load_indices_from_storage,
)

# prompt helper
from llama_index.indices.prompt_helper import PromptHelper

# QueryBundle
from llama_index.indices.query.schema import QueryBundle
from llama_index.indices.service_context import (
    ServiceContext,
    set_global_service_context,
)
from llama_index.indices.tree import GPTTreeIndex, TreeIndex
from llama_index.indices.vector_store import GPTVectorStoreIndex, VectorStoreIndex
from llama_index.llm_predictor import LLMPredictor

# token predictor
from llama_index.llm_predictor.mock import MockLLMPredictor

# prompts
from llama_index.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    # backwards compatibility
    Prompt,
    PromptTemplate,
    SelectorPromptTemplate,
)
from llama_index.readers import SimpleDirectoryReader
from llama_index.readers.download import download_loader

# response
from llama_index.response.schema import Response

# Response Synthesizer
from llama_index.response_synthesizers.factory import get_response_synthesizer

# readers
from llama_index.schema import Document

# storage
from llama_index.storage.storage_context import StorageContext
from llama_index.token_counter.mock_embed_model import MockEmbedding

# sql wrapper
from llama_index.utilities.sql_wrapper import SQLDatabase

# global tokenizer
from llama_index.utils import get_tokenizer, set_global_tokenizer

# best practices for library logging:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger(__name__).addHandler(NullHandler())

__all__ = [
    "StorageContext",
    "ServiceContext",
    "ComposableGraph",
    # indices
    "SummaryIndex",
    "VectorStoreIndex",
    "TreeIndex",
    # indices - legacy names
    "ListIndex",
    "GPTTreeIndex",
    "GPTVectorStoreIndex",
    "Prompt",
    "PromptTemplate",
    "BasePromptTemplate",
    "ChatPromptTemplate",
    "SelectorPromptTemplate",
    "OpenAIEmbedding",
    "SummaryPrompt",
    "TreeInsertPrompt",
    "TreeSelectPrompt",
    "TreeSelectMultiplePrompt",
    "RefinePrompt",
    "QuestionAnswerPrompt",
    "KeywordExtractPrompt",
    "QueryKeywordExtractPrompt",
    "Response",
    "WikipediaReader",
    "ObsidianReader",
    "Document",
    "SimpleDirectoryReader",
    "JSONReader",
    "SimpleMongoReader",
    "NotionPageReader",
    "GoogleDocsReader",
    "MboxReader",
    "SlackReader",
    "StringIterableReader",
    "WeaviateReader",
    "FaissReader",
    "ChromaReader",
    "DeepLakeReader",
    "PineconeReader",
    "PsychicReader",
    "QdrantReader",
    "MilvusReader",
    "DiscordReader",
    "SimpleWebPageReader",
    "RssReader",
    "BeautifulSoupWebReader",
    "TrafilaturaWebReader",
    "LLMPredictor",
    "MockLLMPredictor",
    "VellumPredictor",
    "VellumPromptRegistry",
    "MockEmbedding",
    "SQLDatabase",
    "SQLDocumentContextBuilder",
    "SQLContextBuilder",
    "PromptHelper",
    "IndexStructType",
    "TwitterTweetReader",
    "download_loader",
    "GithubRepositoryReader",
    "load_graph_from_storage",
    "load_index_from_storage",
    "load_indices_from_storage",
    "QueryBundle",
    "get_response_synthesizer",
    "set_global_service_context",
    "set_global_handler",
    "set_global_tokenizer",
    "get_tokenizer",
]

# eval global toggle
from llama_index.callbacks.base_handler import BaseCallbackHandler

global_handler: Optional[BaseCallbackHandler] = None

# NOTE: keep for backwards compatibility
SQLContextBuilder = SQLDocumentContextBuilder

# global service context for ServiceContext.from_defaults()
global_service_context: Optional[ServiceContext] = None

# global tokenizer
global_tokenizer: Optional[Callable[[str], list]] = None
