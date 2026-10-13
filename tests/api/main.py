from fastapi import FastAPI
from multi_agent_system.api.routes.documents import router as documents_router


app = FastAPI(
    title="Multi Agent System API",
    version="1.0.0",
)

app.include_router(documents_router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Multi Agent System API läuft",
    }
