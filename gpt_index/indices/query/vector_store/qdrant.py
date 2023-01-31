"""Qdrant vector store index query."""
from typing import Optional, Dict, Any, cast, List

from gpt_index.data_structs import QdrantIndexStruct, Node
from gpt_index.embeddings.base import BaseEmbedding
from gpt_index.indices.query.embedding_utils import SimilarityTracker
from gpt_index.indices.query.vector_store.base import BaseGPTVectorStoreIndexQuery
from gpt_index.indices.utils import truncate_text


class GPTQdrantIndexQuery(BaseGPTVectorStoreIndexQuery[QdrantIndexStruct]):
    def __init__(
        self,
        index_struct: QdrantIndexStruct,
        embed_model: Optional[BaseEmbedding] = None,
        similarity_top_k: Optional[int] = 1,
        client: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        super().__init__(
            index_struct=index_struct,
            embed_model=embed_model,
            similarity_top_k=similarity_top_k,
            **kwargs,
        )

        import_err_msg = (
            "`qdrant-client` package not found, please run `pip install qdrant-client`"
        )
        try:
            import qdrant_client  # noqa: F401
        except ImportError:
            raise ValueError(import_err_msg)

        if client is None:
            raise ValueError("client cannot be None.")

        self._client = cast(qdrant_client.QdrantClient, client)

    def _get_nodes_for_response(
        self,
        query_str: str,
        verbose: bool = False,
        similarity_tracker: Optional[SimilarityTracker] = None,
    ) -> List[Node]:
        """Get nodes for response."""
        query_embedding = self._embed_model.get_query_embedding(query_str)

        response = self._client.search(
            collection_name=self.index_struct.get_collection_name(),
            query_vector=query_embedding,
            limit=self.similarity_top_k,
        )

        if verbose:
            print(f"> Top {len(response)} nodes:")

        nodes = []
        for point in response:
            node = Node(
                doc_id=point.payload.get("doc_id"),
                text=point.payload.get("text"),
                extra_info=point.payload,
            )
            nodes.append(node)

            if similarity_tracker is not None:
                similarity_tracker.add(node, point.score)

            if verbose:
                print(
                    f"> [Node {point.id}] [Similarity score: {point.score:.6}] "
                    f"{truncate_text(point.payload.get('text'), 100)}"
                )

        return nodes
