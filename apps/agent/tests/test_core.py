from unittest.mock import patch

from admin_template_agent.agent.core import AgentCore


def test_chat():
    with patch.object(AgentCore, "chat", return_value="hi"):
        assert AgentCore().chat("hi") == "hi"
