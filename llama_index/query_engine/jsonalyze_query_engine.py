import json
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from llama_index.core.base_query_engine import BaseQueryEngine
from llama_index.core.response.schema import Response
from llama_index.prompts import BasePromptTemplate, PromptTemplate
from llama_index.prompts.default_prompts import DEFAULT_JSONALYZE_PROMPT
from llama_index.prompts.mixin import PromptDictType, PromptMixinType
from llama_index.prompts.prompt_type import PromptType
from llama_index.schema import QueryBundle
from llama_index.service_context import ServiceContext
from llama_index.utils import print_text

logger = logging.getLogger(__name__)

DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL = (
    "Given a query, synthesize a response based on SQL query results"
    " to satisfy the query. Only include details that are relevant to"
    " the query. If you don't know the answer, then say that.\n"
    "SQL Query: {sql_query}\n"
    "Table Schema: {table_schema}\n"
    "SQL Response: {sql_response}\n"
    "Query: {query_str}\n"
    "Response: "
)

DEFAULT_RESPONSE_SYNTHESIS_PROMPT = PromptTemplate(
    DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL,
    prompt_type=PromptType.SQL_RESPONSE_SYNTHESIS,
)

DEFAULT_TABLE_NAME = "items"


def default_jsonalyzer(
    list_of_dict: List[Dict[str, Any]],
    query: str,
    service_context: ServiceContext,
    table_name: str = DEFAULT_TABLE_NAME,
    prompt: BasePromptTemplate = DEFAULT_JSONALYZE_PROMPT,
) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """Default JSONalyzer that executes a query on a list of dictionaries.

    Args:
        list_of_dict (List[Dict[str, Any]]): List of dictionaries to query.
        query (str): The query to execute.
        prompt (BasePromptTemplate): The prompt to use.
        service_context (Optional[ServiceContext]): The service context.

    Returns:
        Tuple[str, Dict[str, Any], List[Dict[str, Any]]]: The SQL Query,
            the Schema, and the Result.
    """
    try:
        import sqlite_utils
    except ImportError as exc:
        IMPORT_ERROR_MSG = (
            "sqlite-utils is needed to use this Query Engine:\n"
            "pip install sqlite-utils"
        )

        raise ImportError(IMPORT_ERROR_MSG) from exc
    db = sqlite_utils.Database(memory=True)
    try:
        db[table_name].insert_all(list_of_dict)
    except sqlite_utils.db_exceptions.IntegrityError as exc:
        print_text(f"Error inserting into table {table_name}, expected format:")
        print_text("[{col1: val1, col2: val2, ...}, ...]")
        raise ValueError("Invalid list_of_dict") from exc

    table_schema = db[table_name].columns_dict

    sql_query = service_context.llm.predict(
        prompt,
        table_name=table_name,
        table_schema=table_schema,
        question=query,
    )

    try:
        results = list(db.query(sql_query))
    except sqlite_utils.db_exceptions.OperationalError as exc:
        print_text(f"Error executing query: {sql_query}")
        raise ValueError("Invalid query") from exc

    return sql_query, table_schema, results


class JSONalyzeQueryEngine(BaseQueryEngine):
    """JSON List Shape Data Analysis Query Engine.

    Converts natural language statasical queries to JSON Path queries.

    list_of_dict(List[Dict[str, Any]]): List of dictionaries to query.
    service_context (ServiceContext): ServiceContext
    jsonalyze_prompt (BasePromptTemplate): The JSONalyze prompt to use.
    analyzer (Callable): The analyzer that executes the query.
    synthesize_response (bool): Whether to synthesize a response.
    response_synthesis_prompt (BasePromptTemplate): The response synthesis prompt
        to use.
    table_name (str): The table name to use.
    verbose (bool): Whether to print verbose output.
    """

    def __init__(
        self,
        list_of_dict: List[Dict[str, Any]],
        service_context: ServiceContext,
        jsonalyze_prompt: Optional[BasePromptTemplate] = None,
        analyzer: Optional[Callable] = None,
        synthesize_response: bool = True,
        response_synthesis_prompt: Optional[BasePromptTemplate] = None,
        table_name: str = DEFAULT_TABLE_NAME,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        self._list_of_dict = list_of_dict
        self._service_context = service_context
        self._jsonalyze_prompt = jsonalyze_prompt or DEFAULT_JSONALYZE_PROMPT
        self._analyzer = analyzer or default_jsonalyzer
        self._synthesize_response = synthesize_response
        self._response_synthesis_prompt = (
            response_synthesis_prompt or DEFAULT_RESPONSE_SYNTHESIS_PROMPT
        )
        self._table_name = table_name
        self._verbose = verbose

        super().__init__(self._service_context.callback_manager)

    def _get_prompts(self) -> Dict[str, Any]:
        """Get prompts."""
        return {
            "jsonalyze_prompt": self._jsonalyze_prompt,
            "response_synthesis_prompt": self._response_synthesis_prompt,
        }

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "json_path_prompt" in prompts:
            self._json_path_prompt = prompts["json_path_prompt"]
        if "response_synthesis_prompt" in prompts:
            self._response_synthesis_prompt = prompts["response_synthesis_prompt"]

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {}

    def _query(self, query_bundle: QueryBundle) -> Response:
        """Answer an analytical query on the JSON List."""
        query = query_bundle.query_str
        if self._verbose:
            print_text(f"Query: {query}")

        sql_query, table_schema, results = self._analyzer(
            self._list_of_dict,
            query,
            self._service_context,
            table_name=self._table_name,
            prompt=self._jsonalyze_prompt,
        )
        if self._verbose:
            print_text(f"SQL Query: {sql_query}\n")
            print_text(f"Table Schema: {table_schema}\n")
            print_text(f"SQL Response: {results}\n")

        if self._synthesize_response:
            response_str = self._service_context.llm.predict(
                self._response_synthesis_prompt,
                sql_query=sql_query,
                table_schema=table_schema,
                sql_response=results,
                query_str=query_bundle.query_str,
            )
            if self._verbose:
                print_text(f"Response: {response_str}")
        else:
            response_str = json.dumps(
                {
                    "sql_query": sql_query,
                    "table_schema": table_schema,
                    "sql_response": results,
                }
            )
        response_metadata = {"sql_query": sql_query, "table_schema": str(table_schema)}

        return Response(response=response_str, metadata=response_metadata)

    async def _aquery(self, query_bundle: QueryBundle) -> Response:
        """Answer an analytical query on the JSON List."""
        query = query_bundle.query_str
        if self._verbose:
            print_text(f"Query: {query}")

        sql_query, table_schema, results = self._analyzer(
            self._list_of_dict,
            query,
            self._service_context,
            table_name=self._table_name,
            prompt=self._jsonalyze_prompt,
        )
        if self._verbose:
            print_text(f"SQL Query: {sql_query}")
            print_text(f"Table Schema: {table_schema}")
            print_text(f"SQL Response: {results}")

        if self._synthesize_response:
            response_str = await self._service_context.llm.apredict(
                self._response_synthesis_prompt,
                sql_query=sql_query,
                table_schema=table_schema,
                sql_response=results,
                query_str=query_bundle.query_str,
            )
            if self._verbose:
                print_text(f"Response: {response_str}")
        else:
            response_str = json.dumps(
                {
                    "sql_query": sql_query,
                    "table_schema": table_schema,
                    "sql_response": results,
                }
            )
        response_metadata = {"sql_query": sql_query, "table_schema": str(table_schema)}

        return Response(response=response_str, metadata=response_metadata)
