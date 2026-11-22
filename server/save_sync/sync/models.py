"""Closed wire shapes and definition-independent Schema 1 validation."""
from typing import Annotated, Generic, Literal, TypeVar
import unicodedata

from pydantic import BaseModel, ConfigDict, Field, AfterValidator, model_validator

MAX_INT = 2**53 - 1
Natural = Annotated[int, Field(ge=0, le=MAX_INT)]
Positive = Annotated[int, Field(ge=1, le=MAX_INT)]
Cell = Annotated[int, Field(ge=-1, le=MAX_INT)]
Size = Annotated[int, Field(ge=1, le=50)]
PuzzleId = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,128}$")]
Uuid = Annotated[str, Field(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")]
Secret = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{43}$")]
Username = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{2,31}$"), AfterValidator(str.lower)]
Password = Annotated[str, Field(min_length=12, max_length=128)]
ZOOMS = (12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 44, 48, 54, 60, 66, 72)


def device_label(value):
    if any(unicodedata.category(c) == "Cc" for c in value):
        raise ValueError("control character")
    return value


DeviceName = Annotated[str, Field(min_length=1, max_length=64), AfterValidator(device_label)]


class Shape(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Edge(Shape):
    anchor: Literal["grid_end", "outer_start"]


class Middle(Shape):
    anchor: Literal["middle"]
    start: Positive
    end: Positive


class View(Shape):
    center: Annotated[list[float], Field(min_length=2, max_length=2)]
    zoom: Positive
    overview: bool
    active_color: Positive
    tool: Literal["fill", "erase", "hand"]
    row_clue_reads: list[Edge | Middle]
    column_clue_reads: list[Edge | Middle]


class Change(Shape):
    index: Natural
    before: Cell
    after: Cell


class Save(Shape):
    schema_version: Annotated[int, Field(alias="schema", ge=1, le=1)]
    definition_id: PuzzleId
    definition_revision: Positive
    width: Size
    height: Size
    cells: list[Cell]
    history: list[list[Change]]
    cursor: Natural
    undo_used: bool
    completed: bool
    view: View

    @model_validator(mode="after")
    def check_replay(self):
        size = self.width * self.height
        if len(self.cells) != size or self.cursor > len(self.history):
            raise ValueError("dimensions or cursor")
        if self.cursor < len(self.history) and not self.undo_used:
            raise ValueError("redo without undo")
        board = [-1] * size
        colors = {self.view.active_color}
        for step, action in enumerate(self.history):
            if step == self.cursor and board != self.cells:
                raise ValueError("cursor state")
            if not 1 <= len(action) <= size:
                raise ValueError("action size")
            seen = set()
            for change in action:
                i = change.index
                if i >= size or i in seen or change.before == change.after or board[i] != change.before:
                    raise ValueError("invalid history")
                board[i] = change.after
                seen.add(i)
                if change.after > 0:
                    colors.add(change.after)
                    if len(colors) > 8:
                        raise ValueError("palette")
        if self.cursor == len(self.history) and board != self.cells:
            raise ValueError("cursor state")
        x, y = self.view.center
        if not (0 <= x <= self.width and 0 <= y <= self.height and self.view.zoom in ZOOMS):
            raise ValueError("view")
        for lines, count, length in ((self.view.row_clue_reads, self.height, self.width),
                                     (self.view.column_clue_reads, self.width, self.height)):
            if len(lines) != count or any(isinstance(line, Middle) and not line.start < line.end < length for line in lines):
                raise ValueError("clue position")
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
    code: Literal["ok", "conflict_saved", "revision_conflict", "candidate_missing", "history_missing",
                  "conflict_limit", "storage_limit", "sequence_reused", "sequence_stale", "sequence_gap"]
    sequence_consumed: bool


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
    validation: Literal["schema_history_checked"] | None


class Record(Summary, Content):
    pass


class Candidate(CandidateSummary, Content):
    pass


T = TypeVar("T")


class Page(Shape, Generic[T]):
    items: list[T]
    next_cursor: str | None


class Error(Shape):
    code: Literal["malformed_json", "authentication_failed", "not_found", "registration_unavailable",
                  "payload_too_large", "unsupported_media_type", "invalid_request", "rate_limited",
                  "unavailable", "server_generation_changed"]


class Health(Shape):
    status: Literal["ok", "unavailable"]
