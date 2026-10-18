from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from admin_template.core.obs import healthz, readyz

app = FastAPI(title="Admin Template API", version="0.1.0")


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
