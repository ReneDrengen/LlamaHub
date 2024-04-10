import asyncio
from typing import Any, List, Callable

from llama_index.core.async_utils import run_jobs
from llama_index.core.indices.labelled_property_graph.utils import (
    default_parse_triplets_fn,
)
from llama_index.core.prompts import PromptTemplate
from llama_index.core.prompts.default_prompts import (
    DEFAULT_KG_TRIPLET_EXTRACT_PROMPT,
)
from llama_index.core.schema import TransformComponent, BaseNode, NodeRelationship
from llama_index.core.llms.llm import LLM


class ExtractTripletsFromText(TransformComponent):
    """Extract triplets from a graph."""

    llm: LLM
    extract_prompt: PromptTemplate
    parse_fn: Callable
    num_workers: int
    max_triplets_per_chunk: int
    show_progress: bool

    def __init__(
        self,
        llm: LLM,
        extract_prompt: str = None,
        parse_fn: Callable = default_parse_triplets_fn,
        max_triplets_per_chunk: int = 10,
        num_workers: int = 4,
        show_progress: bool = False,
    ) -> None:
        """Init params."""
        super().__init__(
            llm=llm,
            extract_prompt=extract_prompt or DEFAULT_KG_TRIPLET_EXTRACT_PROMPT,
            parse_fn=parse_fn,
            num_workers=num_workers,
            max_triplets_per_chunk=max_triplets_per_chunk,
            show_progress=show_progress,
        )

    @classmethod
    def class_name(cls) -> str:
        return "ExtractTripletsFromText"

    def __call__(self, nodes: List[BaseNode], **kwargs: Any) -> List[BaseNode]:
        """Extract triplets from nodes."""
        return asyncio.run(self.acall(nodes, **kwargs))

    async def _extract(self, node: BaseNode) -> BaseNode:
        """Extract triplets from a node."""
        assert hasattr(node, "text")

        text = node.get_content(metadata_mode="llm")
        try:
            llm_response = await self.llm.apredict(
                self.extract_prompt,
                text=text,
                max_knowledge_triplets=self.max_triplets_per_chunk,
            )
            triplets = self.parse_fn(llm_response)
        except ValueError:
            triplets = []

        existing_triplets = node.metadata.get("triplets", [])
        existing_triplets.extend(triplets)
        node.metadata["triplets"] = existing_triplets

        return node

    async def acall(self, nodes: List[BaseNode], **kwargs: Any) -> List[BaseNode]:
        """Extract triplets from nodes async."""
        jobs = []
        for node in nodes:
            jobs.append(self._extract(node))

        return await run_jobs(
            jobs, workers=self.num_workers, show_progress=self.show_progress
        )


class ExtractTripletsFromNodeRelations(TransformComponent):
    def __call__(self, nodes: List[BaseNode], **kwargs: Any) -> List[BaseNode]:
        """Extract triplets from node relationships."""
        for node in nodes:
            triplets = []

            if node.source_node:
                triplets.append(
                    (node.id_, str(NodeRelationship.SOURCE), node.source_node.node_id)
                )

            if node.parent_node:
                triplets.append(
                    (node.id_, str(NodeRelationship.PARENT), node.parent_node.node_id)
                )

            if node.prev_node:
                triplets.append(
                    (node.id_, str(NodeRelationship.PREVIOUS), node.prev_node.node_id)
                )

            if node.next_node:
                triplets.append(
                    (node.id_, str(NodeRelationship.NEXT), node.next_node.node_id)
                )

            if node.child_nodes:
                for child_node in node.child_nodes:
                    triplets.append(
                        (node.id_, str(NodeRelationship.CHILD), child_node.node_id)
                    )

            existing_triplets = node.metadata.get("triplets", [])
            existing_triplets.extend(triplets)
            node.metadata["triplets"] = existing_triplets

        return nodes
