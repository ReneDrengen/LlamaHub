import os
import pytest
from llama_index.llms.azureai.inference import AzureAIModelInference
from llama_index.core.llms import ChatMessage, MessageRole


@pytest.mark.skipif(
    not set("AZUREAI_ENDPOINT_URL", "AZUREAI_ENDPOINT_CREDENTIAL").issubset(
        set(os.environ)
    ),
    reason="Azure AI endpoint and/or credential are not set.",
)
def test_chat_completion():
    llm = AzureAIModelInference()

    response = llm.chat(
        [
            ChatMessage(
                role="system",
                content="You are a helpful assistant. When you are asked about if this is a test, you always reply 'Yes, this is a test.'",
            ),
            ChatMessage(role="user", content="Is this a test?"),
        ],
        temperature=1.0,
        presence_penalty=0.0,
    )

    assert response.message.role == MessageRole.ASSISTANT
    assert response.message.content.strip() == "Yes, this is a test."
