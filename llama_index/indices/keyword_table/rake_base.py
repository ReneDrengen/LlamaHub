"""RAKE keyword-table based index.

Similar to KeywordTableIndex, but uses RAKE instead of GPT.

"""

from typing import Set

from llama_index.indices.keyword_table.base import BaseKeywordTableIndex
from llama_index.indices.keyword_table.utils import rake_extract_keywords
from llama_index.indices.keyword_table.base import KeywordTableRetrieverMode

class RAKEKeywordTableIndex(BaseKeywordTableIndex):
    """RAKE Keyword Table Index.

    This index uses a RAKE keyword extractor to extract keywords from the text.

    """

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        return rake_extract_keywords(text, max_keywords=self.max_keywords_per_chunk)

    def as_retriever(
        self,
        retriever_mode: Union[
            str, KeywordTableRetrieverMode
        ] = KeywordTableRetrieverMode.RAKE,
        **kwargs: Any,
    ) -> BaseRetriever:
        return super().as_retriever(retriever_mode=retriever_mode, **kwargs)


# legacy
GPTRAKEKeywordTableIndex = RAKEKeywordTableIndex
