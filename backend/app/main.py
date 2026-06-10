import jwt
import sentry_sdk
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRoute
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.websocket.websocket import manager


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )


def _authenticate_websocket_token(token: str) -> bool:
    """Validate the access token of a websocket client.

    Websockets cannot send an Authorization header from the browser, so the
    token is passed as a query parameter instead.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        return False
    with Session(engine) as session:
        user = session.get(User, token_data.sub)
    return user is not None and user.is_active


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = "") -> None:
    if not _authenticate_websocket_token(token):
        await websocket.close(code=1008)
        return
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection open; clients only listen for broadcasts.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


app.include_router(api_router, prefix=settings.API_V1_STR)
