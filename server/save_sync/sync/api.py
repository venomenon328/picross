"""HTTP boundary. FastAPI models describe the same bodies used for runtime validation."""

import json
import math
import os
import re
from decimal import Decimal, DecimalException
from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, FastAPI, Header, Path, Query, Request, Response, Security
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException

from . import auth, store
from . import models as m
from .db import Failure, connect, instance

GEN = "X-Picross-Generation"
PUBLIC = {"register", "login", "recover"}
LISTS = {"puzzles", "history", "conflicts"}
app = FastAPI(
    title="Picross Save Sync", version="1.0", docs_url=None, redoc_url=None, openapi_url="/openapi.json"
)
app.router.redirect_slashes = False


def invalid(_value=None):
    raise ValueError("invalid JSON")


def pairs(items):
    obj = dict(items)
    if len(obj) != len(items):
        invalid()
    return obj


def number(text):
    value = Decimal(text)
    if value == value.to_integral_value() and value.copy_abs() <= m.MAX_INT:
        return int(value)
    result = float(value)
    if not math.isfinite(result):
        invalid()
    return result


def parse(raw):
    try:
        obj = json.loads(
            raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid, parse_float=number
        )
        # Python accepts unpaired escaped surrogates; they are not Unicode scalar values.
        if b"\\u" in raw:
            json.dumps(obj, ensure_ascii=False).encode("utf-8")
        return obj
    except (ValueError, RecursionError, DecimalException, OverflowError):
        raise Failure(400, "malformed_json") from None


class WireRoute(APIRoute):
    def get_route_handler(self):
        endpoint = super().get_route_handler()

        async def checked(request):
            params = request.query_params
            allowed = {"cursor", "limit"} if self.name in LISTS else set()
            if set(params) - allowed or len(params.multi_items()) != len(params):
                raise Failure(422, "invalid_request")
            if "limit" in params and not re.fullmatch(r"[1-9][0-9]?|100", params["limit"]):
                raise Failure(422, "invalid_request")
            if self.name not in PUBLIC:
                header = request.headers.get(GEN, "")
                if not re.fullmatch(
                    r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", header
                ):
                    raise Failure(422, "invalid_request")
                if header != str(request.state.instance["generation"]):
                    raise Failure(409, "server_generation_changed")
            needs_body = request.method == "POST" and self.name != "logout"
            cap = (16 << 20) if self.name == "mutation" else (16 << 10)
            size = request.headers.get("content-length")
            if size and (not size.isascii() or not size.isdigit() or len(size) > 12 or int(size) > cap):
                raise Failure(413, "payload_too_large")
            raw = bytearray()
            async for chunk in request.stream():
                if len(raw) + len(chunk) > cap:
                    raise Failure(413, "payload_too_large")
                raw.extend(chunk)
            if needs_body:
                if (
                    request.headers.get("content-type", "").partition(";")[0].strip().lower()
                    != "application/json"
                    or request.headers.get("content-encoding", "identity").lower() != "identity"
                ):
                    raise Failure(415, "unsupported_media_type")
                request.state.raw = bytes(raw)
                # Supply the bounded bytes and strict parse to FastAPI's body/model reader.
                request._body = request.state.raw
                request._json = parse(request.state.raw)
            elif raw:
                raise Failure(422, "invalid_request")
            return await endpoint(request)

        return checked


def current_instance():
    with connect() as db:
        return instance(db)


origins = [v for v in os.environ.get("SYNC_ORIGINS", "").split(",") if v]
if "*" in origins:
    raise ValueError("Configure exact Web origins")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", GEN],
    expose_headers=[GEN, "Retry-After"],
)


@app.middleware("http")
async def metadata(request, call_next):
    generation = None
    try:
        if request.url.path.startswith("/v1/"):
            request.state.instance = await run_in_threadpool(current_instance)
            generation = str(request.state.instance["generation"])
        response = await call_next(request)
    except (psycopg.Error, Failure):
        response = JSONResponse({"code": "unavailable"}, 503)
    response.headers["Cache-Control"] = "no-store"
    if generation:
        response.headers[GEN] = generation
    return response


@app.exception_handler(Failure)
async def failure(request, exc):
    return JSONResponse({"code": exc.code}, exc.status, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def bad_shape(request, exc):
    return JSONResponse({"code": "invalid_request"}, 422)


@app.exception_handler(HTTPException)
async def unknown(request, exc):
    return JSONResponse({"code": "not_found"}, 404)


@app.get("/health/live", response_model=m.Health)
def live():
    return {"status": "ok"}


@app.get("/health/ready", response_model=m.Health, responses={503: {"model": m.Health}})
def ready():
    try:
        current_instance()
    except (psycopg.Error, Failure):
        return JSONResponse({"status": "unavailable"}, 503)
    return {"status": "ok"}


def require_headers(
    generation: Annotated[m.Uuid, Header(alias=GEN)],
    bearer: Annotated[HTTPAuthorizationCredentials | None, Security(HTTPBearer(auto_error=False))],
):
    # WireRoute validates generation. The session lookup runs inside the operation's transaction.
    if not bearer:
        raise auth.denied()


errors = {s: {"model": m.Error} for s in (400, 401, 404, 409, 413, 415, 422, 429, 503)}
public = APIRouter(prefix="/v1/auth", route_class=WireRoute, responses=errors)
private = APIRouter(
    prefix="/v1", route_class=WireRoute, responses=errors, dependencies=[Depends(require_headers)]
)


def authenticate(request, body, operation):
    auth.throttle(body.username, request.client.host)
    with connect() as db:
        return operation(db, body)


@public.post("/register", status_code=201, response_model=m.Session)
def register(request: Request, body: m.Register):
    return authenticate(request, body, auth.register)


@public.post("/login", response_model=m.Session)
def login(request: Request, body: m.Login):
    return authenticate(request, body, auth.login)


@public.post("/recover", response_model=m.Recovery)
def recover(request: Request, body: m.Recover):
    return authenticate(request, body, auth.recover)


@private.post("/auth/logout", status_code=204)
def logout(request: Request):
    with connect() as db:
        device = auth.session(db, request)
        auth.throttle(device["username"], request.client.host)
        db.execute("UPDATE devices SET token=NULL WHERE device_id=%s", (device["device_id"],))
    return Response(status_code=204)


@private.post("/auth/recovery-code", response_model=m.Recovery)
def recovery_code(request: Request, body: m.Confirm):
    with connect() as db:
        device = auth.session(db, request)
        auth.throttle(device["username"], request.client.host)
        return auth.rotate(db, device, body)


@private.get("/account", response_model=m.Account)
def account(request: Request):
    with connect() as db:
        return auth.info(auth.session(db, request))


def pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    cursor: Annotated[str | None, Query(min_length=1, max_length=1024)] = None,
):
    if cursor is not None and not re.fullmatch(r"[A-Za-z0-9_-]{1,1024}", cursor):
        raise Failure(422, "invalid_request")


@private.get("/puzzles", response_model=m.Page[m.Inventory], dependencies=[Depends(pagination)])
def puzzles(request: Request):
    with connect() as db:
        return store.page(db, auth.session(db, request), request)


@private.get("/puzzles/{puzzle}", response_model=m.Record)
def current(request: Request, puzzle: m.PuzzleId):
    with connect() as db:
        return store.version(db, (auth.session(db, request)["account_id"], puzzle))


@private.get(
    "/puzzles/{puzzle}/history", response_model=m.Page[m.Summary], dependencies=[Depends(pagination)]
)
def history(request: Request, puzzle: m.PuzzleId):
    with connect() as db:
        return store.page(db, auth.session(db, request), request, puzzle, "history")


@private.get("/puzzles/{puzzle}/history/{revision}", response_model=m.Record)
def previous(request: Request, puzzle: m.PuzzleId, revision: Annotated[int, Path(ge=1, le=m.MAX_INT)]):
    with connect() as db:
        return store.version(db, (auth.session(db, request)["account_id"], puzzle), revision)


@private.get(
    "/puzzles/{puzzle}/conflicts",
    response_model=m.Page[m.CandidateSummary],
    dependencies=[Depends(pagination)],
)
def conflicts(request: Request, puzzle: m.PuzzleId):
    with connect() as db:
        return store.page(db, auth.session(db, request), request, puzzle, "conflicts")


@private.get("/puzzles/{puzzle}/conflicts/{candidate_id}", response_model=m.Candidate)
def conflict(request: Request, puzzle: m.PuzzleId, candidate_id: m.Uuid):
    with connect() as db:
        return store.candidate(db, (auth.session(db, request)["account_id"], puzzle), candidate_id)


@private.post(
    "/puzzles/{puzzle}/mutations", response_model=m.Mutation, responses={409: {"model": m.Mutation | m.Error}}
)
def mutation(request: Request, puzzle: m.PuzzleId, body: m.MutationRequest):
    with connect() as db:
        return store.mutate(db, auth.session(db, request), puzzle, body, request)


app.include_router(public)
app.include_router(private)
