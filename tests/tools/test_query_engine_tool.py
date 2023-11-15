"""Test tools."""
from typing import cast

from llama_index.bridge.pydantic import BaseModel
from llama_index.query_engine.custom import CustomQueryEngine
from llama_index.tools.query_engine import QueryEngineTool


class MockQueryEngine(CustomQueryEngine):
    """Custom query engine."""

    def custom_query(self, query_str: str) -> str:
        """Query."""
        return "custom_" + query_str


def test_query_engine_tool() -> None:
    """Test query engine tool."""
    query_engine = MockQueryEngine()

    query_tool = QueryEngineTool.from_defaults(query_engine)

    # make sure both input formats work given function schema that assumes defaults
    response = query_tool("hello world")
    assert str(response) == "custom_hello world"
    response = query_tool(input="foo")
    assert str(response) == "custom_foo"

    fn_schema_cls = query_tool.metadata.fn_schema
    fn_schema_obj = cast(BaseModel, fn_schema_cls(input="bar"))
    response = query_tool(**fn_schema_obj.dict())
    assert str(response) == "custom_bar"
