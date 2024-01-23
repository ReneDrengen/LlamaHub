from typing import Any

from llama_index.callbacks.base_handler import BaseCallbackHandler


def argilla_callback_handler(**kwargs: Any) -> BaseCallbackHandler:
    try:
        from argilla.monitoring.llama_index_handler import ArgillaCallbackHandler
    except ImportError:
        raise ImportError(
            "Please install Argilla with `pip install argilla`"
        )
    return ArgillaCallbackHandler(**kwargs)