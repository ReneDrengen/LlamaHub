"""ClickHouse vector store.

An index that is built on top of an existing ClickHouse cluster.

"""
import importlib
import json
import logging
import re
from typing import Any, Dict, List, Optional, cast

from llama_index.core import ServiceContext
from llama_index.core.schema import (
    BaseNode,
    MetadataMode,
    NodeRelationship,
    RelatedNodeInfo,
    TextNode,
)
from llama_index.core.utils import iter_batch
from llama_index.core.vector_stores.types import (
    VectorStore,
    VectorStoreQuery,
    VectorStoreQueryMode,
    VectorStoreQueryResult,
)
from llama_index.readers.clickhouse.base import (
    DISTANCE_MAPPING,
    ClickHouseSettings,
    escape_str,
    format_list_to_string,
)

logger = logging.getLogger(__name__)


def _default_tokenizer(text: str) -> List[str]:
    """Default tokenizer."""
    tokens = re.split(r"[ \n]", text)  # split by space or newline
    result = []
    for token in tokens:
        if token.strip() == "":
            continue
        result.append(token.strip())
    return result


class ClickHouseVectorStore(VectorStore):
    """ClickHouse Vector Store.
    In this vector store, embeddings and docs are stored within an existing
    ClickHouse cluster.
    During query time, the index uses ClickHouse to query for the top
    k most similar nodes.

    Args:
        clickhouse_client (httpclient): clickhouse-connect httpclient of
            an existing ClickHouse cluster.
        table (str, optional): The name of the ClickHouse table
            where data will be stored. Defaults to "llama_index".
        database (str, optional): The name of the ClickHouse database
            where data will be stored. Defaults to "default".
        index_type (str, optional): The type of the ClickHouse vector index.
            Defaults to "NONE", supported are ("NONE", "HNSW", "ANNOY")
        metric (str, optional): The metric type of the ClickHouse vector index.
            Defaults to "cosine".
        batch_size (int, optional): the size of documents to insert. Defaults to 1000.
        index_params (dict, optional): The index parameters for ClickHouse.
            Defaults to None.
        search_params (dict, optional): The search parameters for a ClickHouse query.
            Defaults to None.
        service_context (ServiceContext, optional): Vector store service context.
            Defaults to None
    """

    stores_text: bool = True
    _table_existed: bool = False
    metadata_column: str = "metadata"
    column_names: List[str]
    column_type_names: List[str]
    AMPLIFY_RATIO_LE5 = 100
    AMPLIFY_RATIO_GT5 = 20
    AMPLIFY_RATIO_GT50 = 10

    def __init__(
        self,
        clickhouse_client: Optional[Any] = None,
        table: str = "llama_index",
        database: str = "default",
        engine: str = "MergeTree",
        index_type: str = "NONE",
        metric: str = "cosine",
        batch_size: int = 1000,
        index_params: Optional[dict] = None,
        search_params: Optional[dict] = None,
        service_context: Optional[ServiceContext] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        import_err_msg = """
            `clickhouse_connect` package not found,
            please run `pip install clickhouse-connect`
        """
        clickhouse_connect_spec = importlib.util.find_spec(
            "clickhouse_connect.driver.httpclient"
        )
        if clickhouse_connect_spec is None:
            raise ImportError(import_err_msg)

        if clickhouse_client is None:
            raise ValueError("Missing ClickHouse client!")
        self._client = clickhouse_client
        self.config = ClickHouseSettings(
            table=table,
            database=database,
            engine=engine,
            index_type=index_type,
            metric=metric,
            batch_size=batch_size,
            index_params=index_params,
            search_params=search_params,
            **kwargs,
        )

        # schema column name, type, and construct format method
        self.column_config: Dict = {
            "id": {"type": "String", "extract_func": lambda x: x.node_id},
            "doc_id": {"type": "String", "extract_func": lambda x: x.ref_doc_id},
            "text": {
                "type": "String",
                "extract_func": lambda x: escape_str(
                    x.get_content(metadata_mode=MetadataMode.NONE) or ""
                ),
            },
            "vector": {
                "type": "Array(Float32)",
                "extract_func": lambda x: x.get_embedding(),
            },
            "node_info": {
                "type": "JSON",
                "extract_func": lambda x: x.get_node_info(),
            },
            "metadata": {
                "type": "String",
                "extract_func": lambda x: json.dumps(x.metadata),
            },
        }
        self.column_names = list(self.column_config.keys())
        self.column_type_names = [
            self.column_config[column_name]["type"] for column_name in self.column_names
        ]

        if service_context is not None:
            service_context = cast(ServiceContext, service_context)
            dimension = len(
                service_context.embed_model.get_query_embedding("try this out")
            )
            self.create_table(dimension)

    @property
    def client(self) -> Any:
        """Get client."""
        return self._client

    def create_table(self, dimension: int) -> None:
        index = ""
        settings = {"allow_experimental_object_type": "1"}
        if self.config.index_type.lower() == "hnsw":
            scalarKind = "f32"
            if self.config.index_params and "ScalarKind" in self.config.index_params:
                scalarKind = self.config.index_params["ScalarKind"]
            index = f"INDEX hnsw_indx vector TYPE usearch('{DISTANCE_MAPPING[self.config.metric]}', '{scalarKind}')"
            settings["allow_experimental_usearch_index"] = "1"
        elif self.config.index_type.lower() == "annoy":
            numTrees = 100
            if self.config.index_params and "NumTrees" in self.config.index_params:
                numTrees = self.config.index_params["NumTrees"]
            index = f"INDEX annoy_indx vector TYPE annoy('{DISTANCE_MAPPING[self.config.metric]}', {numTrees})"
            settings["allow_experimental_annoy_index"] = "1"
        schema_ = f"""
            CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.table}(
                {",".join([f'{k} {v["type"]}' for k, v in self.column_config.items()])},
                CONSTRAINT vector_length CHECK length(vector) = {dimension},
                {index}
            ) ENGINE = MergeTree ORDER BY id
            """
        self.dim = dimension
        self._client.command(schema_, settings=settings)
        self._table_existed = True

    def _upload_batch(
        self,
        batch: List[BaseNode],
    ) -> None:
        _data = []
        # we assume all rows have all columns
        for idx, item in enumerate(batch):
            _row = []
            for column_name in self.column_names:
                _row.append(self.column_config[column_name]["extract_func"](item))
            _data.append(_row)

        self._client.insert(
            f"{self.config.database}.{self.config.table}",
            data=_data,
            column_names=self.column_names,
            column_type_names=self.column_type_names,
        )

    def _build_text_search_statement(
        self, query_str: str, similarity_top_k: int
    ) -> str:
        # TODO: We could make this overridable
        tokens = _default_tokenizer(query_str)
        terms_pattern = [f"\\b(?i){x}\\b" for x in tokens]
        column_keys = self.column_config.keys()
        return (
            f"SELECT {','.join(filter(lambda k: k != 'vector', column_keys))}, "
            f"score FROM {self.config.database}.{self.config.table} WHERE score > 0 "
            f"ORDER BY length(multiMatchAllIndices(text, {terms_pattern})) "
            f"AS score DESC, "
            f"log(1 + countMatches(text, '\\b(?i)({'|'.join(tokens)})\\b')) "
            f"AS d2 DESC limit {similarity_top_k}"
        )

    def _build_hybrid_search_statement(
        self, stage_one_sql: str, query_str: str, similarity_top_k: int
    ) -> str:
        # TODO: We could make this overridable
        tokens = _default_tokenizer(query_str)
        terms_pattern = [f"\\b(?i){x}\\b" for x in tokens]
        column_keys = self.column_config.keys()
        return (
            f"SELECT {','.join(filter(lambda k: k != 'vector', column_keys))}, "
            f"score FROM ({stage_one_sql}) tempt "
            f"ORDER BY length(multiMatchAllIndices(text, {terms_pattern})) "
            f"AS d1 DESC, "
            f"log(1 + countMatches(text, '\\\\b(?i)({'|'.join(tokens)})\\\\b')) "
            f"AS d2 DESC limit {similarity_top_k}"
        )

    def _append_meta_filter_condition(
        self, where_str: Optional[str], exact_match_filter: list
    ) -> str:
        filter_str = " AND ".join(
            f"JSONExtractString("
            f"{self.metadata_column}, '{filter_item.key}') "
            f"= '{filter_item.value}'"
            for filter_item in exact_match_filter
        )
        if where_str is None:
            where_str = filter_str
        else:
            where_str = " AND " + filter_str
        return where_str

    def add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """Add nodes to index.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings
        """
        if not nodes:
            return []

        if not self._table_existed:
            self.create_table(len(nodes[0].get_embedding()))

        for batch in iter_batch(nodes, self.config.batch_size):
            self._upload_batch(batch=batch)

        return [result.node_id for result in nodes]

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.

        Args:
            ref_doc_id (str): The doc_id of the document to delete.
        """
        self._client.command(
            f"DELETE FROM {self.config.database}.{self.config.table} WHERE doc_id='{ref_doc_id}'"
        )

    def drop(self) -> None:
        """Drop ClickHouse table."""
        self._client.command(
            f"DROP TABLE IF EXISTS {self.config.database}.{self.config.table}"
        )

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """Query index for top k most similar nodes.

        Args:
            query (VectorStoreQuery): query
        """
        query_embedding = cast(List[float], query.query_embedding)
        where_str = (
            f"doc_id IN {format_list_to_string(query.doc_ids)}"
            if query.doc_ids
            else None
        )
        # TODO: Support other filter types
        if query.filters is not None and len(query.filters.legacy_filters()) > 0:
            where_str = self._append_meta_filter_condition(
                where_str, query.filters.legacy_filters()
            )

        # build query sql
        if query.mode == VectorStoreQueryMode.DEFAULT:
            query_statement = self.config.build_query_statement(
                query_embed=query_embedding,
                where_str=where_str,
                limit=query.similarity_top_k,
            )
        elif query.mode == VectorStoreQueryMode.HYBRID:
            if query.query_str is not None:
                amplify_ratio = self.AMPLIFY_RATIO_LE5
                if 5 < query.similarity_top_k < 50:
                    amplify_ratio = self.AMPLIFY_RATIO_GT5
                if query.similarity_top_k > 50:
                    amplify_ratio = self.AMPLIFY_RATIO_GT50
                query_statement = self._build_hybrid_search_statement(
                    self.config.build_query_statement(
                        query_embed=query_embedding,
                        where_str=where_str,
                        limit=query.similarity_top_k * amplify_ratio,
                    ),
                    query.query_str,
                    query.similarity_top_k,
                )
                logger.debug(f"hybrid query_statement={query_statement}")
            else:
                raise ValueError("query_str must be specified for a hybrid query.")
        elif query.mode == VectorStoreQueryMode.TEXT_SEARCH:
            if query.query_str is not None:
                query_statement = self._build_text_search_statement(
                    query.query_str,
                    query.similarity_top_k,
                )
                logger.debug(f"text query_statement={query_statement}")
            else:
                raise ValueError("query_str must be specified for a text query.")
        else:
            raise ValueError(f"query mode {query.mode!s} not supported")
        nodes = []
        ids = []
        similarities = []
        response = self._client.query(query_statement)
        column_names = response.column_names
        id_idx = column_names.index("id")
        text_idx = column_names.index("text")
        metadata_idx = column_names.index("metadata")
        node_info_idx = column_names.index("node_info")
        score_idx = column_names.index("score")
        for r in response.result_rows:
            start_char_idx = None
            end_char_idx = None

            if isinstance(r[node_info_idx], dict):
                start_char_idx = r[node_info_idx].get("start", None)
                end_char_idx = r[node_info_idx].get("end", None)
            node = TextNode(
                id_=r[id_idx],
                text=r[text_idx],
                metadata=json.loads(r[metadata_idx]),
                start_char_idx=start_char_idx,
                end_char_idx=end_char_idx,
                relationships={
                    NodeRelationship.SOURCE: RelatedNodeInfo(node_id=r[id_idx])
                },
            )

            nodes.append(node)
            similarities.append(r[score_idx])
            ids.append(r[id_idx])
        return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)
