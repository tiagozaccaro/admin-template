from datetime import UTC, datetime

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from admin_template.core.settings import settings


def get_agent(model: str) -> Agent:
    base_url = settings.kilo_api_base
    api_key = settings.kilo_api_key
    kilo_model = settings.kilo_model or model
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    agent_model = OpenAIModel(kilo_model, provider=provider)

    agent = Agent(agent_model, system_prompt="You are a helpful admin assistant.")

    @agent.tool
    async def get_current_time(ctx: RunContext) -> str:
        """Return the current server time."""
        return datetime.now(UTC).isoformat()

    return agent
