import asyncio
import json
from contextlib import suppress
from functools import partial
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph.graph import build_auth_app, build_guest_app
from graph.state import AgentState
from utils.websocket import (
    create_session,
    get_session_meta,
    push_client_message,
    receive_session_event,
    reset_current_session,
    set_current_session,
    set_session_meta,
    subscribe_session,
    unsubscribe_session,
)
from utils.session import (
    AUTH_COOKIE_KEY,
    create_login_token,
    load_user_conf,
    resolve_user_from_token,
    revoke_token,
)

APPS = {
    "guest": build_guest_app(),
    "auth": build_auth_app(),
}
DEFAULT_APP_KEY = "guest"
_session_workers: dict[str, asyncio.Task[None]] = {}


class LoginBody(BaseModel):
    username: str
    password: str


def _normalize_app_key(app_key: str) -> str:
    key = str(app_key or "").strip().lower()
    if key not in APPS:
        raise ValueError(f"unsupported app graph: {app_key}")
    return key


def _parse_incoming_message(message: str) -> object:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return {"type": "text", "text": message}


async def _forward_messages_to_fastapi_websocket(
    websocket: WebSocket,
    queue: asyncio.Queue[str],
) -> None:
    while True:
        message = await queue.get()
        try:
            await websocket.send_text(message)
        except Exception:
            return


async def run_session(session_id: str) -> None:
    token = set_current_session(session_id)
    try:
        while True:
            event = await receive_session_event("user_input", session_id=session_id)
            text = str(event.get("text") or "").strip()
            if not text:
                continue

            app_key = str(
                get_session_meta(session_id, "app_key", DEFAULT_APP_KEY)
            ).strip().lower()
            graph_app = APPS.get(app_key, APPS[DEFAULT_APP_KEY])
            state: AgentState = {"raw_input": text}
            async for _ in graph_app.astream(state, stream_mode="values"):
                pass
    finally:
        reset_current_session(token)


def _on_session_worker_done(session_id: str, task: asyncio.Task[None]) -> None:
    current = _session_workers.get(session_id)
    if current is task:
        _session_workers.pop(session_id, None)

    with suppress(asyncio.CancelledError):
        task.exception()


def ensure_session_worker(session_id: str, app_key: str) -> asyncio.Task[None]:
    normalized_session = create_session(session_id)
    normalized_app = _normalize_app_key(app_key)
    bound_app = get_session_meta(normalized_session, "app_key")
    if bound_app is None:
        set_session_meta(normalized_session, app_key=normalized_app)
    elif str(bound_app).strip().lower() != normalized_app:
        raise ValueError(
            f"session '{normalized_session}' already bound to app '{bound_app}', "
            f"cannot switch to '{normalized_app}'"
        )

    existing = _session_workers.get(normalized_session)
    if existing is not None and not existing.done():
        return existing

    worker = asyncio.create_task(
        run_session(normalized_session),
        name=f"doover-session-{normalized_session}",
    )
    worker.add_done_callback(partial(_on_session_worker_done, normalized_session))
    _session_workers[normalized_session] = worker
    return worker


async def stop_session_workers() -> None:
    workers = [task for task in _session_workers.values() if not task.done()]
    for task in workers:
        task.cancel()

    for task in workers:
        with suppress(asyncio.CancelledError):
            await task

    _session_workers.clear()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        await stop_session_workers()


app = FastAPI(title="DoOver Graph Router", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"ok": "true"}


@app.websocket("/ws/{app_key}")
async def ws_by_app(
    ws: WebSocket,
    app_key: str,
    session_id: str = Query(..., min_length=1),
) -> None:
    await ws.accept()
    try:
        normalized_app = _normalize_app_key(app_key)
        normalized_session = create_session(session_id)
        if normalized_app == "auth":
            user_name = await resolve_user_from_token(ws.cookies.get(AUTH_COOKIE_KEY))
            if not user_name:
                raise ValueError("auth websocket requires login")
        ensure_session_worker(normalized_session, normalized_app)
    except (RuntimeError, ValueError) as exc:
        await ws.close(code=1008, reason=str(exc))
        return

    outbound_queue = subscribe_session(normalized_session)
    forward_task = asyncio.create_task(
        _forward_messages_to_fastapi_websocket(ws, outbound_queue)
    )
    try:
        while True:
            message = await ws.receive_text()
            parsed = _parse_incoming_message(message)
            await push_client_message(parsed, session_id=normalized_session)
    except Exception:
        return
    finally:
        forward_task.cancel()
        with suppress(asyncio.CancelledError):
            await forward_task
        unsubscribe_session(outbound_queue, session_id=normalized_session)


@app.websocket("/ws")
async def ws_default(
    ws: WebSocket,
    session_id: str = Query(..., min_length=1),
) -> None:
    user_name = await resolve_user_from_token(ws.cookies.get(AUTH_COOKIE_KEY))
    target_app = "auth" if user_name else "guest"
    await ws_by_app(ws, target_app, session_id)


@app.post("/login")
async def login(body: LoginBody, response: Response) -> dict[str, bool]:
    conf = load_user_conf()
    expected_user = conf["user_name"]
    expected_key = conf["user_key"]
    if not expected_user or not expected_key:
        raise HTTPException(status_code=500, detail="user config is invalid")
    if body.username != expected_user or body.password != expected_key:
        await asyncio.sleep(5)
        raise HTTPException(status_code=401, detail="bad credentials")
    token = await create_login_token(expected_user)
    response.set_cookie(
        key=AUTH_COOKIE_KEY,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return {"ok": True}


@app.post("/logout")
async def logout(request: Request, response: Response) -> dict[str, bool]:
    await revoke_token(request.cookies.get(AUTH_COOKIE_KEY))
    response.delete_cookie(key=AUTH_COOKIE_KEY, path="/")
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("test:app", host="0.0.0.0", port=8000, reload=False)
