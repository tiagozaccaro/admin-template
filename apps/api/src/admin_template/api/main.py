from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from admin_template.api.v1.router import router as v1_router
from admin_template.auth.router import router as auth_router
from admin_template.core.obs import healthz, readyz
from admin_template.core.settings import settings

app = FastAPI(title="Admin Template API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/healthz")
async def healthz_live():
    """Liveness probe: the process is up."""
    return await healthz()


@app.get("/readyz")
async def readyz_ready():
    """Readiness probe: DB and Redis reachability."""
    result = await readyz()
    ready = bool(result.get("ready", False))
    return JSONResponse(
        content=result,
        status_code=status.HTTP_200_OK
        if ready
        else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


__all__ = ["app"]
