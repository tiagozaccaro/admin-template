from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from admin_template.api.v1.routers.integrations import router as integrations_router
from admin_template.api.v1.routers.sync import router as sync_router
from admin_template.core.middleware.idempotency import IdempotencyMiddleware
from admin_template.core.obs import healthz, readyz

app = FastAPI(title="Admin Template API", version="0.1.0")

app.add_middleware(IdempotencyMiddleware)

app.include_router(integrations_router)
app.include_router(sync_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/healthz")
async def healthz_live():
    """Liveness probe: the process is up."""
    return await healthz()


@app.get("/readyz")
async def readyz_ready():
    """Readiness probe: DB, Redis, Keycloak reachability."""
    result = await readyz()
    ready = bool(result.get("ready", False))
    return JSONResponse(
        content=result,
        status_code=status.HTTP_200_OK
        if ready
        else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


__all__ = ["app"]
