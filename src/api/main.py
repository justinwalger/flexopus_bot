"""Entry point for the API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.memory import InMemorySaver

from api.routes import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Replace InMemorySaver with a persistent checkpointer (e.g., database-backed)
    # for production use (probably overkill)

    checkpointer = InMemorySaver()

    app.state.checkpointer = checkpointer
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(chat.router, prefix="/api")
