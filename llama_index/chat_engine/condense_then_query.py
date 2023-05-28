import logging
from typing import Any, List, Optional, Tuple

from llama_index.chat_engine.types import BaseChatEngine
from llama_index.chat_engine.utils import get_chat_history
from llama_index.indices.query.base import BaseQueryEngine
from llama_index.indices.service_context import ServiceContext
from llama_index.prompts.base import Prompt
from llama_index.response.schema import RESPONSE_TYPE

logger = logging.getLogger(__name__)


DEFAULT_TEMPLATE = """\
Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History: {chat_history}

Follow Up Input: {question}

Standalone question:"""

DEFAULT_PROMPT = Prompt(DEFAULT_TEMPLATE)


class CondenseQuestionChatEngine(BaseChatEngine):
    """Condense question chat engine.

    First generate a standalone question from conversation context and last message,
    then query the query engine for a response.
    """

    def __init__(
        self,
        query_engine: BaseQueryEngine,
        condense_question_prompt: Optional[str] = None,
        chat_history: List[Tuple[str, str]] = None,
        service_context: Optional[ServiceContext] = None,
        verbose: bool = False,
    ) -> None:
        self._query_engine = query_engine
        self._condense_question_prompt = condense_question_prompt or DEFAULT_PROMPT
        self._chat_history = chat_history or []
        self._service_context = service_context or ServiceContext.from_defaults()
        self._verbose = verbose

    @classmethod
    def from_defaults(
        cls,
        query_engine: BaseQueryEngine,
        condense_question_prompt: Optional[str] = None,
        chat_history: List[Tuple[str, str]] = None,
        service_context: Optional[ServiceContext] = None,
        verbose: bool = False,
        **kwargs: Any,
    ):
        return cls(
            query_engine,
            condense_question_prompt,
            chat_history,
            service_context,
            verbose=verbose,
        )

    def _condense_question(self, chat_history: List[str], last_message: str) -> str:
        """
        Generate standalone question from conversation context and last message.
        """

        chat_history_str = get_chat_history(chat_history)
        logger.debug(chat_history_str)

        response, _ = self._service_context.llm_predictor.predict(
            self._condense_question_prompt,
            question=last_message,
            chat_history=chat_history_str,
        )
        return response

    def _acondense_question(self, chat_history: List[str], last_message: str) -> str:
        """
        Generate standalone question from conversation context and last message.
        """

        chat_history_str = get_chat_history(chat_history)
        logger.debug(chat_history_str)

        response, _ = self._service_context.llm_predictor.apredict(
            self._condense_question_prompt,
            question=last_message,
            chat_history=chat_history_str,
        )
        return response

    def chat(self, message: str) -> RESPONSE_TYPE:
        # Generate standalone question from conversation context and last message
        condensed_question = self._condense_question(self._chat_history, message)

        log_str = f"Querying with: {condensed_question}"
        logger.info(log_str)
        if self._verbose:
            print(log_str)

        # Query with standalone question
        response = self._query_engine.query(condensed_question)

        # Record response
        self._chat_history.append((message, str(response)))
        return response

    async def achat(self, message: str) -> RESPONSE_TYPE:
        # Generate standalone question from conversation context and last message
        condensed_question = await self._acondense_question(self._chat_history, message)

        log_str = f"Querying with: {condensed_question}"
        logger.info(log_str)
        if self._verbose:
            print(log_str)

        # Query with standalone question
        response = await self._query_engine.aquery(condensed_question)

        # Record response
        self._chat_history.append((message, str(response)))
        return response

    def reset(self) -> None:
        # Clear chat history
        self._chat_history = []
