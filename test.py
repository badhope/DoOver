import asyncio
import json
from contextlib import suppress
from functools import partial
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph.graph import build_auth_app, build_guest_app
from graph.state import AgentState
from user.update_name_pswd import update_username_and_password
from utils.load_config import load_json_config, save_json_config
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

class ActivateLLMBody(BaseModel):
    provider: str
    model: str | None = None


class AddProviderBody(BaseModel):
    provider: str
    type: str = "openai"
    base_url: str
    api_key: str
    models: list[str]
    set_active: bool = False


class AddModelBody(BaseModel):
    provider: str
    model: str
    set_active: bool = False


class DeleteProviderBody(BaseModel):
    provider: str



class DeleteModelBody(BaseModel):
    provider: str
    model: str

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

#修改用户名密码
@app.put("/update_user")
async def update_user(request: Request, user: LoginBody) -> dict[str, bool]:
    token = request.cookies.get(AUTH_COOKIE_KEY)
    if not token or not resolve_user_from_token(token):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        await update_username_and_password(token, user.username, user.password)
    except Exception as e:
        raise e
    return {"ok": True}

PROVIDER_CONFIG_PATH = Path("llm/config/provider.json")

#更换llm_model
@app.put("/update_llm")
async def update_llm(request: Request, payload: ActivateLLMBody) -> dict[str, str]:
    token = request.cookies.get(AUTH_COOKIE_KEY)
    user_name = await resolve_user_from_token(token) if token else None
    if not user_name:
        raise HTTPException(status_code=401, detail="not logged in")

    provider = payload.provider.strip()
    if not provider:
        raise HTTPException(status_code=400, detail="provider is required")

    data = load_json_config(PROVIDER_CONFIG_PATH)
    providers = data.get("llm_providers")
    if not isinstance(providers, dict) or provider not in providers:
        raise HTTPException(status_code=400, detail="provider not found")

    provider_conf = providers[provider]
    models = provider_conf.get("models")
    if not isinstance(models, list) or not models:
        raise HTTPException(status_code=400, detail="provider has no models")

    if payload.model and payload.model.strip():
        model = payload.model.strip()
    else:
        model = str(models[0])

    if model not in models:
        raise HTTPException(status_code=400, detail="model not in provider models")

    data["active_llm_provider"] = provider
    data["active_llm_model"] = model
    save_json_config(PROVIDER_CONFIG_PATH, data)

    return {"provider": provider, "model": model}



async def _require_login_token(request: Request) -> str:
    token = request.cookies.get(AUTH_COOKIE_KEY)
    if not token or not await resolve_user_from_token(token):
        raise HTTPException(status_code=401, detail="not logged in")
    return token


@app.put("/add_llm_provider")
async def add_llm_provider(request: Request, payload: AddProviderBody) -> dict[str, str]:
    await _require_login_token(request)

    provider = payload.provider.strip()
    if not provider:
        raise HTTPException(status_code=400, detail="provider is required")

    models = [m.strip() for m in payload.models if str(m).strip()]
    if not models:
        raise HTTPException(status_code=400, detail="models is required")

    data = load_json_config(PROVIDER_CONFIG_PATH)
    providers = data.get("llm_providers")
    if not isinstance(providers, dict):
        raise HTTPException(status_code=500, detail="invalid provider config")

    if provider in providers:
        raise HTTPException(status_code=400, detail="provider already exists")

    providers[provider] = {
        "type": payload.type.strip() or "openai",
        "base_url": payload.base_url.strip(),
        "api_key": payload.api_key.strip(),
        "models": models,
    }

    if payload.set_active:
        data["active_llm_provider"] = provider
        data["active_llm_model"] = models[0]

    save_json_config(PROVIDER_CONFIG_PATH, data)
    return {"provider": provider, "model": models[0]}


@app.put("/add_llm_model")
async def add_llm_model(request: Request, payload: AddModelBody) -> dict[str, str]:
    await _require_login_token(request)

    provider = payload.provider.strip()
    model = payload.model.strip()
    if not provider or not model:
        raise HTTPException(status_code=400, detail="provider and model are required")

    data = load_json_config(PROVIDER_CONFIG_PATH)
    providers = data.get("llm_providers")
    if not isinstance(providers, dict) or provider not in providers:
        raise HTTPException(status_code=400, detail="provider not found")

    provider_conf = providers[provider]
    models = provider_conf.get("models")
    if not isinstance(models, list):
        raise HTTPException(status_code=500, detail="invalid provider models")

    if model not in models:
        models.append(model)

    if payload.set_active:
        data["active_llm_provider"] = provider
        data["active_llm_model"] = model

    save_json_config(PROVIDER_CONFIG_PATH, data)
    return {"provider": provider, "model": model}


@app.delete("/delete_llm_provider")
async def delete_llm_provider(request: Request, payload: DeleteProviderBody) -> dict[str, str]:
    await _require_login_token(request)

    provider = payload.provider.strip()
    if not provider:
        raise HTTPException(status_code=400, detail="provider is required")

    data = load_json_config(PROVIDER_CONFIG_PATH)
    providers = data.get("llm_providers")
    if not isinstance(providers, dict) or provider not in providers:
        raise HTTPException(status_code=400, detail="provider not found")

    if len(providers) <= 1:
        raise HTTPException(status_code=400, detail="cannot delete last provider")

    active_provider = str(data.get("active_llm_provider") or "").strip()
    if active_provider == provider:
        raise HTTPException(status_code=400, detail="provider is currently active")

    del providers[provider]
    save_json_config(PROVIDER_CONFIG_PATH, data)
    return {"deleted_provider": provider}


@app.delete("/delete_llm_model")
async def delete_llm_model(request: Request, payload: DeleteModelBody) -> dict[str, str]:
    await _require_login_token(request)

    provider = payload.provider.strip()
    model = payload.model.strip()
    if not provider or not model:
        raise HTTPException(status_code=400, detail="provider and model are required")

    data = load_json_config(PROVIDER_CONFIG_PATH)
    providers = data.get("llm_providers")
    if not isinstance(providers, dict) or provider not in providers:
        raise HTTPException(status_code=400, detail="provider not found")

    provider_conf = providers[provider]
    models = provider_conf.get("models")
    if not isinstance(models, list) or model not in models:
        raise HTTPException(status_code=400, detail="model not found")

    if len(models) <= 1:
        raise HTTPException(status_code=400, detail="cannot delete last model in provider")

    active_provider = str(data.get("active_llm_provider") or "").strip()
    active_model = str(data.get("active_llm_model") or "").strip()
    if active_provider == provider and active_model == model:
        raise HTTPException(status_code=400, detail="model is currently active")

    models.remove(model)
    save_json_config(PROVIDER_CONFIG_PATH, data)
    return {"provider": provider, "deleted_model": model}

if __name__ == "__main__":
    uvicorn.run("test:app", host="0.0.0.0", port=8000, reload=False)
