from unittest import mock

import pytest
from ai21.models import (
    CompletionsResponse as J2CompletionResponse,
    CompletionData,
    Completion,
    CompletionFinishReason,
    Prompt,
    RoleType,
    ChatMessage as J2ChatMessage,
    ChatResponse as J2ChatResponse,
    ChatOutput,
)
from ai21.models.chat import (
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionChunk,
    ChoicesChunk,
    ChoiceDelta,
    ChatMessage as AI21ChatMessage,
)
from ai21.models.usage_info import UsageInfo
from llama_index.core.base.llms.base import BaseLLM
from llama_index.core.base.llms.types import ChatResponse, CompletionResponse
from llama_index.core.llms import ChatMessage

from llama_index.llms.ai21 import AI21

_PROMPT = "What is the meaning of life?"
_FAKE_API_KEY = "fake-api-key"
_MODEL_NAME = "jamba-instruct"
_FAKE_CHAT_COMPLETIONS_RESPONSE = ChatCompletionResponse(
    id="some_id",
    choices=[
        ChatCompletionResponseChoice(
            index=0,
            message=AI21ChatMessage(role="assistant", content="42"),
        )
    ],
    usage=UsageInfo(
        prompt_tokens=10,
        completion_tokens=10,
        total_tokens=20,
    ),
)

_FAKE_STREAM_CHUNKS = [
    ChatCompletionChunk(
        id="some_id_0",
        choices=[
            ChoicesChunk(index=0, delta=ChoiceDelta(role="assistant", content=""))
        ],
    ),
    ChatCompletionChunk(
        id="some_id_1",
        choices=[ChoicesChunk(index=0, delta=ChoiceDelta(role=None, content="42"))],
    ),
]

_FAKE_RAW_COMPLETION_RESPONSE = {
    "id": "1",
    "prompt": {"text": "What is the meaning of life?", "tokens": None},
    "completions": [
        {
            "data": {"text": "42", "tokens": None},
            "finishReason": {
                "reason": None,
                "length": None,
            },
        }
    ],
}

_FAKE_COMPLETION_RESPONSE = CompletionResponse(
    text="42",
    raw=_FAKE_RAW_COMPLETION_RESPONSE,
)


def test_text_inference_embedding_class():
    names_of_base_classes = [b.__name__ for b in AI21.__mro__]
    assert BaseLLM.__name__ in names_of_base_classes


def test_chat():
    messages = ChatMessage(role="user", content="What is the meaning of life?")
    expected_chat_response = ChatResponse(
        message=ChatMessage(role="assistant", content="42"),
        raw=_FAKE_CHAT_COMPLETIONS_RESPONSE.to_dict(),
    )

    with mock.patch("llama_index.llms.ai21.base.AI21Client"):
        llm = AI21(api_key=_FAKE_API_KEY)

    llm._client.chat.completions.create.return_value = _FAKE_CHAT_COMPLETIONS_RESPONSE

    actual_response = llm.chat(messages=[messages])

    assert actual_response == expected_chat_response

    llm._client.chat.completions.create.assert_called_once_with(
        messages=[AI21ChatMessage(role="user", content="What is the meaning of life?")],
        stream=False,
        **llm._get_all_kwargs(),
    )


def test_chat__when_j2():
    j2_response = J2ChatResponse(
        outputs=[ChatOutput(text="42", role=RoleType.ASSISTANT, finish_reason=None)],
    )
    expected_chat_response = ChatResponse(
        message=ChatMessage(role="assistant", content="42"),
        raw=j2_response.to_dict(),
    )

    with mock.patch("llama_index.llms.ai21.base.AI21Client"):
        llm = AI21(api_key=_FAKE_API_KEY, model="j2-ultra")

    llm._client.chat.create.return_value = j2_response

    actual_response = llm.chat(messages=[ChatMessage(role="user", content=_PROMPT)])

    assert actual_response == expected_chat_response

    llm._client.chat.create.assert_called_once_with(
        messages=[J2ChatMessage(role=RoleType.USER, text=_PROMPT)],
        stream=False,
        **llm._get_all_kwargs(),
    )


def test_stream_chat():
    messages = ChatMessage(role="user", content="What is the meaning of life?")

    with mock.patch("llama_index.llms.ai21.base.AI21Client"):
        llm = AI21(api_key=_FAKE_API_KEY)

    llm._client.chat.completions.create.return_value = _FAKE_STREAM_CHUNKS

    actual_response = llm.stream_chat(messages=[messages])

    expected_chunks = [
        ChatResponse(
            message=ChatMessage(role="assistant", content=""),
            delta="",
            raw=_FAKE_STREAM_CHUNKS[0].to_dict(),
        ),
        ChatResponse(
            message=ChatMessage(role="assistant", content="42"),
            delta="42",
            raw=_FAKE_STREAM_CHUNKS[1].to_dict(),
        ),
    ]

    assert list(actual_response) == expected_chunks

    llm._client.chat.completions.create.assert_called_once_with(
        messages=[AI21ChatMessage(role="user", content="What is the meaning of life?")],
        stream=True,
        **llm._get_all_kwargs(),
    )


def test_complete():
    expected_chat_response = CompletionResponse(
        text="42",
        raw=_FAKE_CHAT_COMPLETIONS_RESPONSE.to_dict(),
    )

    with mock.patch("llama_index.llms.ai21.base.AI21Client"):
        llm = AI21(api_key=_FAKE_API_KEY)

    llm._client.chat.completions.create.return_value = _FAKE_CHAT_COMPLETIONS_RESPONSE

    actual_response = llm.complete(prompt="What is the meaning of life?")

    assert actual_response == expected_chat_response

    # Since we actually call chat.completions - check that the call was made to it
    llm._client.chat.completions.create.assert_called_once_with(
        messages=[AI21ChatMessage(role="user", content="What is the meaning of life?")],
        stream=False,
        **llm._get_all_kwargs(),
    )
    llm._client.completion.assert_not_called()


def test_complete__when_j2():
    prompt = "What is the meaning of life?"

    with mock.patch("llama_index.llms.ai21.base.AI21Client"):
        llm = AI21(api_key=_FAKE_API_KEY, model="j2-ultra")

    expected_response = J2CompletionResponse(
        id="1",
        completions=[
            Completion(
                data=CompletionData(text="42"), finish_reason=CompletionFinishReason()
            )
        ],
        prompt=Prompt(text=prompt),
    )

    llm._client.completion.create.return_value = expected_response

    actual_response = llm.complete(prompt=prompt)

    assert actual_response == _FAKE_COMPLETION_RESPONSE

    # Since we actually call chat.completions - check that the call was made to it
    llm._client.completion.create.assert_called_once_with(
        prompt=prompt,
        stream=False,
        **llm._get_all_kwargs(),
    )


def test_stream_complete():
    expected_stream_completion_chunks_response = [
        CompletionResponse(text="", delta="", raw=_FAKE_STREAM_CHUNKS[0].to_dict()),
        CompletionResponse(text="42", delta="42", raw=_FAKE_STREAM_CHUNKS[1].to_dict()),
    ]

    with mock.patch("llama_index.llms.ai21.base.AI21Client"):
        llm = AI21(api_key=_FAKE_API_KEY)

    llm._client.chat.completions.create.return_value = _FAKE_STREAM_CHUNKS

    actual_response = llm.stream_complete(prompt="What is the meaning of life?")

    assert list(actual_response) == expected_stream_completion_chunks_response

    # Since we actually call chat.completions - check that the call was made to it
    llm._client.chat.completions.create.assert_called_once_with(
        messages=[AI21ChatMessage(role="user", content="What is the meaning of life?")],
        stream=True,
        **llm._get_all_kwargs(),
    )


def test_stream_complete_when_j2__should_raise_error():
    llm = AI21(api_key=_FAKE_API_KEY, model="j2-ultra")

    with pytest.raises(ValueError):
        llm.stream_complete(prompt="What is the meaning of life?")


def test_chat_complete_when_j2__should_raise_error():
    llm = AI21(api_key=_FAKE_API_KEY, model="j2-ultra")

    with pytest.raises(ValueError):
        llm.stream_chat(
            messages=[ChatMessage(role="user", content="What is the meaning of life?")]
        )
