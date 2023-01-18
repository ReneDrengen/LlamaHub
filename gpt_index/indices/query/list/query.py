"""Default query for GPTListIndex."""
from typing import List, Any

from gpt_index.data_structs.data_structs import IndexList, Node
from gpt_index.indices.query.base import BaseGPTIndexQuery


class BaseGPTListIndexQuery(BaseGPTIndexQuery[IndexList]):
    """GPTListIndex query.

    Arguments are shared among subclasses.

    Args:
        text_qa_template (Optional[QuestionAnswerPrompt]): A Question Answering Prompt
            (see :ref:`Prompt-Templates`).
        refine_template (Optional[RefinePrompt]): A Refinement Prompt
            (see :ref:`Prompt-Templates`).

    """


class GPTListIndexQuery(BaseGPTListIndexQuery):
    """GPTListIndex query.

    The default query mode for GPTListIndex, which traverses
    each node in sequence and synthesizes a response across all nodes
    (with an optional keyword filter).
    Set when `mode="default"` in `query` method of `GPTListIndex`.

    .. code-block:: python

        response = index.query("<query_str>", mode="default")

    See BaseGPTListIndexQuery for arguments.

    """

    def _get_nodes_for_response(
        self, query_str: str, verbose: bool = False, **nodes_kwargs: Any
    ) -> List[Node]:
        """Get nodes for response."""
        return self.index_struct.nodes
