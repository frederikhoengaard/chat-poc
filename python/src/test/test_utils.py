import pytest
from backend.models import Conversation, Message
from backend.utils import create_messages
from langchain.schema import AIMessage, HumanMessage, SystemMessage

test_message = Message(
    **{"role": "assistant", "content": "Hi there, how can I help you?"}
)
test_conversation = Conversation(**{"conversation": [test_message]})


@pytest.mark.parametrize(
    "conversation, expected_role", [(test_conversation, AIMessage)]
)
def test_create_messages(conversation, expected_role):
    assert isinstance(create_messages(conversation.conversation)[-1], expected_role)
