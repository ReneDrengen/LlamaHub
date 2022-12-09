"""General prompt helper that can help deal with token limitations.

The helper can split text. It can also concatenate text from Node
structs but keeping token limitations in mind.

"""

from gpt_index.langchain_helpers.text_splitter import TokenTextSplitter
from gpt_index.prompts.base import Prompt
from gpt_index.indices.data_structs import Node
from gpt_index.constants import MAX_CHUNK_OVERLAP, MAX_CHUNK_SIZE, NUM_OUTPUTS
from gpt_index.utils import globals_helper
from typing import Optional, List


class PromptHelper:
    """Prompt helper."""

    def __init__(
        self,
        max_input_size: int = MAX_CHUNK_SIZE,
        num_output: int = NUM_OUTPUTS,
        max_chunk_overlap: int = MAX_CHUNK_OVERLAP,
        embedding_limit: Optional[int] = None,
    ) -> None:
        """Init params."""
        self.max_input_size = max_input_size
        self.num_output = num_output
        self.max_chunk_overlap = max_chunk_overlap
        self.embedding_limit = embedding_limit

    def get_chunk_size_given_prompt(self, prompt: str, num_chunks: int, padding: Optional[int] = 1) -> int:
        """Get chunk size making sure we can also fit the prompt in.

        Chunk size is computed based on a function of the total input size, the prompt length,
        the number of outputs, and the number of chunks.
        
        If padding is specified, then we subtract that from the chunk size.
        By default we assume there is a padding of 1 (for the newline between chunks).
        
        """
        tokenizer = globals_helper.tokenizer
        prompt_tokens = tokenizer(prompt)
        num_prompt_tokens = len(prompt_tokens["input_ids"])

        # NOTE: if embedding limit is specified, then chunk_size must not be larger than
        # embedding_limit
        result = (self.max_input_size - num_prompt_tokens - self.num_output) // num_chunks
        if padding is not None:
            result -= padding

        if self.embedding_limit is not None:
            return min(result, self.embedding_limit)
        else:
            return result

    def get_text_splitter_given_prompt(
        self,
        prompt: Prompt,
        num_chunks: int,
    ) -> TokenTextSplitter:
        """Get text splitter given prompt.

        Allows us to get the text splitter which will split up text according
        to the desired chunk size.

        """
        
        fmt_dict = {v: "" for v in prompt.input_variables}
        prompt.format(**fmt_dict)
        chunk_size = self.get_chunk_size_given_prompt(
            prompt,
            num_chunks,
        )
        text_splitter = TokenTextSplitter(
            separator=" ",
            chunk_size=chunk_size,
            chunk_overlap=self.max_chunk_overlap // num_chunks,
        )
        return text_splitter


    def get_text_from_nodes(
        self, node_list: List[Node], prompt: Optional[Prompt] = None
    ) -> str:
        """Get text from nodes. Used by tree-structured indices."""
        num_nodes = len(node_list)
        chunk_size = None
        if prompt is not None:
            # add padding given the newline character
            chunk_size = self.get_chunk_size_given_prompt(
                prompt,
                num_nodes,
                padding=1,
            )
        results = []
        for node in node_list:
            text = node.text[:chunk_size] if chunk_size is not None else node.text
            results.append(text)
        return "\n".join(results)


    def get_numbered_text_from_nodes(
        self, node_list: List[Node], prompt: Optional[Prompt] = None
    ) -> str:
        """Get text from nodes in the format of a numbered list.

        Used by tree-structured indices.

        """
        num_nodes = len(node_list)
        chunk_size = None
        if prompt is not None:
            # add padding given the number, and the newlines
            chunk_size = self.get_chunk_size_given_prompt(
                prompt,
                num_nodes,
                padding=5,
            )
        results = []
        number = 1
        for node in node_list:
            text = f"({number}) {' '.join(node.text.splitlines())}"
            if chunk_size is not None:
                text = text[:chunk_size]
            results.append()
        return "\n\n".join(results)
