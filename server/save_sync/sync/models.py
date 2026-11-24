"""Closed wire shapes and definition-independent progress validation."""

import unicodedata
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

MAX_INT = 2**53 - 1
Natural = Annotated[int, Field(ge=0, le=MAX_INT)]
Positive = Annotated[int, Field(ge=1, le=MAX_INT)]
Cell = Annotated[int, Field(ge=-1, le=MAX_INT)]
Size = Annotated[int, Field(ge=1, le=50)]
PuzzleId = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,128}$")]
Uuid = Annotated[str, Field(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")]
Secret = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{43}$")]
Username = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{2,31}$"), AfterValidator(str.lower)]
def password_bytes(value: str) -> str:
    if len(value.encode("utf-8")) > 1024:
        raise ValueError("password byte length")
    return value


Password = Annotated[str, Field(min_length=8, max_length=128), AfterValidator(password_bytes)]

def device_label(value):
    if any(unicodedata.category(c) == "Cc" for c in value):
        raise ValueError("control character")
    return value


DeviceName = Annotated[str, Field(min_length=1, max_length=64), AfterValidator(device_label)]


class Shape(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Save(Shape):
    format: Literal["picross-progress/v1"]
    definition_id: PuzzleId
    definition_revision: Positive
    width: Size
    height: Size
    cells: list[Cell]
    undo_used: bool
    completed: bool

    @model_validator(mode="after")
    def check_cells(self):
        if len(self.cells) != self.width * self.height:
            raise ValueError("cell count")
        if len({cell for cell in self.cells if cell > 0}) > 8:
            raise ValueError("palette")
        return self


class Register(Shape):
    username: Username
    password: Password
    invitation: Secret
    device_name: DeviceName


class Login(Shape):
    username: Username
    password: Password
    device_id: Uuid | None
    device_name: DeviceName


class Recover(Shape):
    username: Username
    new_password: Password
    recovery_code: Secret


class Confirm(Shape):
    password: Password


class Recovery(Shape):
    recovery_code: Secret


class Account(Shape):
    account_id: Uuid
    username: str
    device_id: Uuid
    last_request_seq: Natural


class Session(Account):
    token: Secret
    expires_at: str
    recovery_code: Secret | None


class RequestBase(Shape):
    format: Literal["picross-sync/v1"]
    request_seq: Positive
    base_server_revision: Natural


class Snapshot(RequestBase):
    operation: Literal["snapshot"]
    save: Save


class Reset(RequestBase):
    operation: Literal["reset"]
    definition_revision: Positive


class Choose(RequestBase):
    operation: Literal["resolve", "discard"]
    candidate_id: Uuid


class Restore(RequestBase):
    operation: Literal["restore"]
    history_revision: Positive


MutationRequest = Annotated[Snapshot | Reset | Choose | Restore, Field(discriminator="operation")]


class Mutation(Shape):
    format: Literal["picross-sync/v1"]
    request_seq: Positive
    outcome: Literal["applied", "conflict", "discarded", "rejected"]
    server_revision: Natural
    candidate_id: Uuid | None
    code: Literal[
        "ok",
        "conflict_saved",
        "revision_conflict",
        "candidate_missing",
        "history_missing",
        "conflict_limit",
        "storage_limit",
        "sequence_reused",
        "sequence_stale",
        "sequence_gap",
        "request_abandoned",
    ]
    sequence_consumed: bool


class Abandon(Shape):
    format: Literal["picross-request-abandon/v1"]
    request_seq: Positive
    expected_last_request_seq: Natural
    request_hash: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    puzzle_id: PuzzleId

    @model_validator(mode="after")
    def next_sequence(self):
        if self.request_seq != self.expected_last_request_seq + 1:
            raise ValueError("sequence does not follow expected checkpoint")
        return self


class Checkpoint(Shape):
    format: Literal["picross-device-checkpoint/v1"]
    account_id: Uuid
    device_id: Uuid
    last_request_seq: Natural
    last_request_hash: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None
    response_status: Literal[200, 409] | None
    response_body: str | None


class Inventory(Shape):
    puzzle_id: PuzzleId
    server_revision: Natural
    conflict_count: Natural


class Entry(Shape):
    puzzle_id: PuzzleId
    definition_revision: Positive
    kind: Literal["snapshot", "reset"]
    device_id: Uuid
    device_name: DeviceName


class Summary(Entry):
    server_revision: Positive
    updated_at: str


class CandidateSummary(Entry):
    base_server_revision: Natural
    candidate_id: Uuid
    created_at: str


class Content(Shape):
    save: Save | None
    validation: Literal["progress_structure_checked"] | None


class Record(Summary, Content):
    pass


class Candidate(CandidateSummary, Content):
    pass


T = TypeVar("T")


class Page(Shape, Generic[T]):
    items: list[T]
    next_cursor: str | None


class Error(Shape):
    code: Literal[
        "malformed_json",
        "authentication_failed",
        "not_found",
        "registration_unavailable",
        "payload_too_large",
        "unsupported_media_type",
        "invalid_request",
        "rate_limited",
        "unavailable",
        "server_generation_changed",
        "sequence_reused",
        "sequence_stale",
        "sequence_gap",
    ]


class Health(Shape):
    status: Literal["ok", "unavailable"]
