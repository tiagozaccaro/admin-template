import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from admin_template.core.settings import settings
from admin_template.modules.chat.agent import get_agent
from admin_template.modules.chat.schemas import ChatRequest
from admin_template.modules.chat.session import load_history, save_history

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/models")
async def list_models():
    return json.loads(settings.chat_models)


@router.post("/agent")
async def chat_agent(req: ChatRequest):
    session_id = req.session_id or "default"
    history = await load_history(session_id)
    agent = get_agent(req.model)

    async def gen():
        prompt = req.prompt_input
        if history:
            prompt = (
                "\n".join(f"{m['role']}: {m['content']}" for m in history)
                + "\nuser: "
                + req.prompt_input
            )
        async with agent.run_stream(prompt) as stream:
            collected = ""
            async for chunk in stream.stream_text(delta=True):
                collected += chunk
                yield f"data: {chunk}\n\n"
            history.append({"role": "user", "content": req.prompt_input})
            history.append({"role": "assistant", "content": collected})
            await save_history(session_id, history)
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
