"""Utils for keyword table."""

import re
from typing import Optional, Set

import nltk
import pandas as pd
from nltk.corpus import stopwords

from gpt_index.indices.utils import expand_tokens_with_subtokens


def simple_extract_keywords(
    text_chunk: str, max_keywords: Optional[int] = None, filter_stopwords: bool = True
) -> Set[str]:
    """Extract keywords with simple algorithm."""
    tokens = [t.strip().lower() for t in re.findall(r"\w+", text_chunk)]
    if filter_stopwords:
        tokens = [t for t in tokens if t not in stopwords.words("english")]
    value_counts = pd.Series(tokens).value_counts()
    keywords = value_counts.index.tolist()[:max_keywords]
    return set(keywords)


def rake_extract_keywords(
    text_chunk: str,
    max_keywords: Optional[int] = None,
    expand_with_subtokens: bool = True,
) -> Set[str]:
    """Extract keywords with RAKE."""
    nltk.download("punkt")
    try:
        from rake_nltk import Rake
    except ImportError:
        raise ImportError("Please install rake_nltk: `pip install rake_nltk`")

    r = Rake()
    r.extract_keywords_from_text(text_chunk)
    keywords = r.get_ranked_phrases()[:max_keywords]
    if expand_with_subtokens:
        return set(expand_tokens_with_subtokens(keywords))
    else:
        return set(keywords)


def extract_keywords_given_response(response: str, lowercase: bool = True) -> Set[str]:
    """Extract keywords given the GPT-generated response.

    Used by keyword table indices.

    """
    results = []
    keywords = response.split(",")
    for k in keywords:
        if "KEYWORD" in k:
            continue
        rk = k
        if lowercase:
            rk = rk.lower()
        results.append(rk.strip())

    # if keyword consists of multiple words, split into subwords
    # (removing stopwords)
    return expand_tokens_with_subtokens(set(results))
