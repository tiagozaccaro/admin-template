from admin_template_agent.agent.core import AgentCore

def test_chat():
    assert AgentCore().chat("hi") == "hi"
