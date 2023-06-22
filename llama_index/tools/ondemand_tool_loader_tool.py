"""Ad-hoc data loader tool.

Tool that wraps any other tool, and is able to load data on-demand.

"""


from llama_hub.tools.types import BaseTool, ToolMetadata
from typing import Any, Optional, Dict, Type
from llama_index.indices.base import BaseIndex
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.tools.utils import create_schema_from_function
from pydantic import BaseModel
from llama_index.tools.function_tool import FunctionTool


class OnDemandToolLoaderTool(BaseTool):
    """On-demand function tool loader.

    Loads data by calling the passed function tool, stores in index, and queries
    for relevant data with a natural language query string.
    """

    def __init__(
        self,
        tool: FunctionTool,
        index_cls: Type[BaseIndex],
        index_kwargs: Dict,
        metadata: ToolMetadata,
        use_query_str_in_loader: bool = False,
        query_str_kwargs_key: str = "query_str",
    ) -> None:
        """Init params."""
        self._tool = tool
        self._index_cls = index_cls
        self._index_kwargs = index_kwargs
        self._use_query_str_in_loader = use_query_str_in_loader
        self._metadata = metadata
        self._query_str_kwargs_key = query_str_kwargs_key

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata

    @classmethod
    def from_defaults(
        cls,
        tool: FunctionTool,
        index_cls: Optional[Type[BaseIndex]] = None,
        index_kwargs: Optional[Dict] = None,
        use_query_str_in_loader: bool = False,
        query_str_kwargs_key: str = "query_str",
        name: Optional[str] = None,
        description: Optional[str] = None,
        fn_schema: Optional[Type[BaseModel]] = None,
    ) -> "OnDemandToolLoaderTool":
        """From defaults."""
        # NOTE: fn_schema should be specified if you want to use as langchain Tool

        index_cls = index_cls or VectorStoreIndex
        index_kwargs = index_kwargs or {}
        if description is None:
            description = f"Tool to load data from {tool.__class__.__name__}"
        if fn_schema is None:
            fn_schema = create_schema_from_function(
                name, tool._fn, [(query_str_kwargs_key, str, None)]
            )
        metadata = ToolMetadata(name=name, description=description, fn_schema=fn_schema)
        return cls(
            tool=tool,
            index_cls=index_cls,
            index_kwargs=index_kwargs,
            use_query_str_in_loader=use_query_str_in_loader,
            query_str_kwargs_key=query_str_kwargs_key,
            metadata=metadata,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call."""
        if self._query_str_kwargs_key not in kwargs:
            raise ValueError(
                "Missing query_str in kwargs with parameter name: "
                f"{self._query_str_kwargs_key}"
            )
        if self._use_query_str_in_loader:
            query_str = kwargs[self._query_str_kwargs_key]
        else:
            query_str = kwargs.pop(self._query_str_kwargs_key)
        docs = self._tool(*args, **kwargs)
        index = self._index_cls.from_documents(docs, **self._index_kwargs)
        # TODO: add query kwargs
        query_engine = index.as_query_engine()
        response = query_engine.query(query_str)
        return str(response)

