from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt_input: str
    model: str
    session_id: str | None = None
