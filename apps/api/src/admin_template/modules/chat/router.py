import os
import tempfile

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai_harness import FileSystem, Shell

from admin_template.core.settings import settings


def make_model(name: str | None = None) -> OpenAIChatModel:
    return OpenAIChatModel(
        name or settings.kilo_model,
        provider=OpenAIProvider(
            base_url=settings.kilo_api_base,
            api_key=settings.kilo_api_key,
        ),
    )


router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None


@router.post("/chat")
async def chat(req: ChatRequest):
    workspace = os.path.join(tempfile.gettempdir(), "admin-template-agent")
    os.makedirs(workspace, exist_ok=True)
    agent = Agent(
        make_model(req.model),
        capabilities=[FileSystem(workspace), Shell(cwd=workspace)],
    )
    prompt = req.messages[-1].get("content", "") if req.messages else ""
    result = await agent.run(prompt)
    return {"reply": result.output}
