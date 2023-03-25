"""Query runner."""

from typing import Any, Dict, List, Optional, Union, cast

from gpt_index.data_structs.data_structs_v2 import V2IndexStruct as IndexStruct
from gpt_index.docstore import DocumentStore
from gpt_index.indices.query.base import BaseGPTIndexQuery, BaseQueryRunner
from gpt_index.indices.query.query_combiner.base import (
    BaseQueryCombiner,
    get_default_query_combiner,
)
from gpt_index.indices.query.query_transform.base import (
    BaseQueryTransform,
    IdentityQueryTransform,
)
from gpt_index.indices.query.schema import QueryBundle, QueryConfig, QueryMode
from gpt_index.indices.registry import IndexRegistry
from gpt_index.indices.service_context import ServiceContext
from gpt_index.response.schema import Response

# TMP: refactor query config type
QUERY_CONFIG_TYPE = Union[Dict, QueryConfig]


class QueryRunner(BaseQueryRunner):
    """Tool to take in a query request and perform a query with the right classes.

    Higher-level wrapper over a given query.

    """

    def __init__(
        self,
        service_context: ServiceContext,
        docstore: DocumentStore,
        index_registry: IndexRegistry,
        query_configs: Optional[List[QUERY_CONFIG_TYPE]] = None,
        query_transform: Optional[BaseQueryTransform] = None,
        query_combiner: Optional[BaseQueryCombiner] = None,
        recursive: bool = False,
        use_async: bool = False,
    ) -> None:
        """Init params."""
        type_to_config_dict: Dict[str, QueryConfig] = {}
        id_to_config_dict: Dict[str, QueryConfig] = {}
        if query_configs is None or len(query_configs) == 0:
            query_config_objs: List[QueryConfig] = []
        elif isinstance(query_configs[0], Dict):
            query_config_objs = [
                QueryConfig.from_dict(cast(Dict, qc)) for qc in query_configs
            ]
        else:
            query_config_objs = [cast(QueryConfig, q) for q in query_configs]

        for qc in query_config_objs:
            type_to_config_dict[qc.index_struct_type] = qc
            if qc.index_struct_id is not None:
                id_to_config_dict[qc.index_struct_id] = qc

        self._type_to_config_dict = type_to_config_dict
        self._id_to_config_dict = id_to_config_dict
        self._service_context = service_context
        self._docstore = docstore
        self._index_registry = index_registry
        self._query_transform = query_transform or IdentityQueryTransform()
        self._query_combiner = query_combiner
        self._recursive = recursive
        self._use_async = use_async

    def _get_query_kwargs(self, config: QueryConfig) -> Dict[str, Any]:
        """Get query kwargs.

        Also update with default arguments if not present.

        """
        query_kwargs = {k: v for k, v in config.query_kwargs.items()}
        if "prompt_helper" not in query_kwargs:
            query_kwargs["prompt_helper"] = self._prompt_helper
        if "llm_predictor" not in query_kwargs:
            query_kwargs["llm_predictor"] = self._llm_predictor
        if "embed_model" not in query_kwargs:
            query_kwargs["embed_model"] = self._embed_model
        return query_kwargs

    def _get_query_config(self, index_struct: IndexStruct) -> QueryConfig:
        """Get query config."""
        index_struct_id = index_struct.get_doc_id()
        index_struct_type = index_struct.get_type()
        if index_struct_id in self._id_to_config_dict:
            config = self._id_to_config_dict[index_struct_id]
        elif index_struct_type in self._type_to_config_dict:
            config = self._type_to_config_dict[index_struct_type]
        else:
            config = QueryConfig(
                index_struct_type=index_struct_type, query_mode=QueryMode.DEFAULT
            )
        return config

    def _get_query_transform(self, index_struct: IndexStruct) -> BaseQueryTransform:
        """Get query transform."""
        config = self._get_query_config(index_struct)
        if config.query_transform is not None:
            query_transform = cast(BaseQueryTransform, config.query_transform)
        else:
            query_transform = self._query_transform
        return query_transform

    def _get_query_combiner(
        self, index_struct: IndexStruct, query_transform: BaseQueryTransform
    ) -> BaseQueryCombiner:
        """Get query transform."""
        config = self._get_query_config(index_struct)
        if config.query_combiner is not None:
            query_combiner: Optional[BaseQueryCombiner] = cast(
                BaseQueryCombiner, config.query_combiner
            )
        else:
            query_combiner = self._query_combiner

        # if query_combiner is still None, use default
        if query_combiner is None:
            extra_kwargs = {
                "llm_predictor": self._llm_predictor,
            }
            query_combiner = get_default_query_combiner(
                index_struct, query_transform, extra_kwargs=extra_kwargs
            )

        return cast(BaseQueryCombiner, query_combiner)

    def _get_query_obj(
        self,
        index_struct: IndexStruct,
    ) -> BaseGPTIndexQuery:
        """Get query object."""
        index_struct_type = index_struct.get_type()
        config = self._get_query_config(index_struct)
        mode = config.query_mode

        query_cls = self._index_registry.type_to_query[index_struct_type][mode]
        # if recursive, pass self as query_runner to each individual query
        query_runner = self
        query_kwargs = self._get_query_kwargs(config)
        query_obj = query_cls(
            index_struct,
            **query_kwargs,
            query_runner=query_runner,
            docstore=self._docstore,
            recursive=self._recursive,
            use_async=self._use_async,
        )

        return query_obj

    def query(
        self,
        query_str_or_bundle: Union[str, QueryBundle],
        index_struct: IndexStruct,
    ) -> Response:
        """Run query."""
        # NOTE: Currently, query transform is only run once
        # TODO: Consider refactor to support index-specific query transform
        # TODO: abstract query transformation loop into a separate class

        query_transform = self._get_query_transform(index_struct)
        query_combiner = self._get_query_combiner(index_struct, query_transform)

        query_obj = self._get_query_obj(index_struct)
        if isinstance(query_str_or_bundle, str):
            query_bundle = QueryBundle(
                query_str=query_str_or_bundle,
                custom_embedding_strs=[query_str_or_bundle],
            )
        else:
            query_bundle = query_str_or_bundle

        return query_combiner.run(query_obj, query_bundle)
        # return query_obj.query(query_bundle)

    async def aquery(
        self,
        query_str_or_bundle: Union[str, QueryBundle],
        index_struct: IndexStruct,
    ) -> Response:
        """Run query."""
        # NOTE: Currently, query transform is only run once
        # TODO: Consider refactor to support index-specific query transform
        query_transform = self._get_query_transform(index_struct)
        transform_extra_info = {"index_struct": index_struct}
        query_bundle = query_transform(
            query_str_or_bundle, extra_info=transform_extra_info
        )
        query_obj = self._get_query_obj(index_struct)

        return await query_obj.aquery(query_bundle)
