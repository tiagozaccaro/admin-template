from fastapi import APIRouter
router = APIRouter()
@router.post("/chat")
def chat(payload: dict):
    return {"reply": payload.get("message", "")}
