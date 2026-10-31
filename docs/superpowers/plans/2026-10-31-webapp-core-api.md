# TechGap Web App — Plan A: Core API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Standing rule:** the commit steps below run only when the user asks. The working tree has substantial unrelated uncommitted work, so always `git add` exact paths, never `git add .` or `-A`.

**Goal:** Build the backend core: a validated release format (v0 draft), a deterministic mock release, a database loader with an active-release pointer, and the public read API, so the frontend can be built against mock data before the pipeline exists.

**Architecture:** A release is an immutable directory (manifest with SHA-256 per file, result sets, scoring bundles, evidence, courses). `read_release` validates it, `load_release` imports it in one transaction, `activate_release` moves a single pointer. FastAPI serves read-only endpoints over SQLAlchemy Core tables (SQLite in tests, Postgres on Supabase). Spec: `docs/superpowers/specs/2026-10-31-techgap-frontend-backend-design.md`.

**Tech Stack:** Python 3.13 (venv), FastAPI, SQLAlchemy 2.0 Core, Pydantic v2, pytest, httpx.

**Revised 2026-10-31** for the contract's decisions on group status (P1), bounds (P2), ranking (P4) and public display of jobs (P8): link statuses are only `supported` and `unresolved`; groups carry `requirement_unresolved`; roles carry a display name; job evidence is title, company, URL and the short extracted phrase only.

**Out of scope for this plan (see the plan index):** student scoring and its endpoints (Plan D; its rules are now decided in the contract), upload and auth, buckets and workflow dispatch, release retention, learning-resource import, the frontend.

**Release format v0 is a DRAFT.** It is agreed with the data-flow session later (open item P9, and the capability-key rule P6). The models are small and isolated in `release_format.py` for that reason.

---

## File structure

All new, under `webapp/api/` (repo root: `techgap-final/`):

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Package metadata, dependencies, pytest config |
| `.gitignore` | Ignore venv, caches, local databases (local file, so the root `.gitignore` stays untouched) |
| `techgap_api/__init__.py` | Package marker |
| `techgap_api/release_format.py` | Pydantic models for a release directory, `read_release` with hash and path checks, `ReleaseError` |
| `techgap_api/mock_release.py` | `write_mock_release`: deterministic mock release with the edge cases |
| `techgap_api/db.py` | SQLAlchemy tables, `normalize_database_url`, `engine_from_env`, `init_db` |
| `techgap_api/loader.py` | `load_release`, `activate_release`, `active_release_id` |
| `techgap_api/app.py` | `create_app(engine)` with the public read endpoints |
| `techgap_api/cli.py` | Developer commands: `mock`, `load`, `activate` |
| `techgap_api/main.py` | Uvicorn entry point (`techgap_api.main:app`) |
| `tests/conftest.py` | `engine` and `release_dir` fixtures |
| `tests/test_db.py`, `test_release_format.py`, `test_mock_release.py`, `test_loader.py`, `test_api.py`, `test_cli.py` | One file per module |
| `docs/plan/RELEASE_FORMAT.md` | The interface document for the pipeline session (Task 6) |

Commands run from the repo root in Git Bash. The venv Python is `webapp/api/.venv/Scripts/python`.

---

### Task 1: Scaffold, database tables, fixtures

**Files:**
- Create: `webapp/api/pyproject.toml`, `webapp/api/.gitignore`, `webapp/api/techgap_api/__init__.py`, `webapp/api/techgap_api/db.py`, `webapp/api/tests/conftest.py`, `webapp/api/tests/test_db.py`

- [ ] **Step 1: Create a branch and the environment**

```bash
git switch -c feature/webapp-core
mkdir -p webapp/api/techgap_api webapp/api/tests
py -3.13 -m venv webapp/api/.venv
```

Expected: the branch is created with the working tree unchanged (`git status --short` still lists the existing changes).

- [ ] **Step 2: Write the packaging files**

`webapp/api/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "techgap-api"
version = "0.0.1"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115,<1",
    "uvicorn>=0.30",
    "sqlalchemy>=2.0,<2.1",
    "pydantic>=2.7,<3",
]

[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.2"]
dev = ["pytest>=8", "httpx>=0.27"]

[tool.setuptools.packages.find]
include = ["techgap_api*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`webapp/api/.gitignore`:

```
.venv/
__pycache__/
.pytest_cache/
*.egg-info/
*.db
```

`webapp/api/techgap_api/__init__.py`: an empty file.

- [ ] **Step 3: Install**

```bash
webapp/api/.venv/Scripts/python -m pip install -e "webapp/api[dev]"
```

Expected: ends with `Successfully installed ... techgap-api-0.0.1 ...`. The version pins above were not checked against the package index; if pip reports a conflict, loosen the pin that it names and note the change.

- [ ] **Step 4: Write the failing tests**

`webapp/api/tests/conftest.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from techgap_api.db import metadata


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    metadata.create_all(eng)
    return eng


@pytest.fixture
def release_dir(tmp_path):
    from techgap_api.mock_release import write_mock_release

    return write_mock_release(tmp_path / "mock")
```

`webapp/api/tests/test_db.py`:

```python
from sqlalchemy import inspect

from techgap_api.db import normalize_database_url


def test_create_all_makes_every_table(engine):
    assert set(inspect(engine).get_table_names()) == {
        "releases",
        "app_state",
        "result_sets",
        "scoring_bundles",
        "evidence",
        "release_courses",
    }


def test_database_url_gets_the_psycopg_driver():
    assert normalize_database_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_database_url("postgresql://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_database_url("sqlite:///x.db") == "sqlite:///x.db"
```

- [ ] **Step 5: Run to verify failure**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Expected: error `ModuleNotFoundError: No module named 'techgap_api.db'`.

- [ ] **Step 6: Implement `db.py`**

`webapp/api/techgap_api/db.py`:

```python
"""Tables for the result releases the app serves.

ponytail: create_all at start-up; add Alembic when the schema must change after the first deploy.
"""
import os

from sqlalchemy import JSON, Column, ForeignKey, Integer, MetaData, String, Table, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine

JsonType = JSON().with_variant(JSONB(), "postgresql")

metadata = MetaData()

releases = Table(
    "releases",
    metadata,
    Column("release_id", String, primary_key=True),
    Column("created_at", String, nullable=False),
    Column("job_cutoff", String, nullable=False),
    Column("syllabus_version", String, nullable=False),
    Column("rule_version", String, nullable=False),
    Column("purpose", String),
    Column("status", String, nullable=False),  # ready | building | failed
    Column("manifest", JsonType, nullable=False),
)

app_state = Table(
    "app_state",
    metadata,
    Column("id", Integer, primary_key=True),  # always row 1
    Column("active_release_id", String, ForeignKey("releases.release_id")),
)

result_sets = Table(
    "result_sets",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("release_id", String, ForeignKey("releases.release_id"), nullable=False),
    Column("pool", String, nullable=False),
    Column("cohort", String, nullable=False),
    Column("scope_type", String, nullable=False),
    Column("scope_id", String, nullable=False),
    Column("window_start", String, nullable=False),
    Column("window_end", String, nullable=False),
    Column("payload", JsonType, nullable=False),
)

scoring_bundles = Table(
    "scoring_bundles",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("release_id", String, ForeignKey("releases.release_id"), nullable=False),
    Column("pool", String, nullable=False),
    Column("cohort", String, nullable=False),
    Column("role_id", String, nullable=False),
    Column("role_name", String, nullable=False),
    Column("payload", JsonType, nullable=False),
)

evidence = Table(
    "evidence",
    metadata,
    Column("release_id", String, ForeignKey("releases.release_id"), primary_key=True),
    Column("ref", String, primary_key=True),
    Column("kind", String, nullable=False),
    Column("source_id", String, nullable=False),
    Column("url", String),
    Column("title", String),  # posting only
    Column("company", String),  # posting only
    Column("source_field", String),  # syllabus only
    Column("text", Text, nullable=False),
)

release_courses = Table(
    "release_courses",
    metadata,
    Column("release_id", String, ForeignKey("releases.release_id"), primary_key=True),
    Column("course_code", String, primary_key=True),
    Column("payload", JsonType, nullable=False),
)


def normalize_database_url(url: str) -> str:
    """Supabase hands out postgres:// or postgresql:// URLs; SQLAlchemy needs the driver named."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def engine_from_env() -> Engine:
    url = os.environ.get("DATABASE_URL", "sqlite:///techgap.db")
    return create_engine(normalize_database_url(url), pool_pre_ping=True)


def init_db(engine: Engine) -> None:
    metadata.create_all(engine)
```

- [ ] **Step 7: Run to verify pass**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Expected: `2 passed`.

- [ ] **Step 8: Commit (only when the user asks)**

```bash
git add webapp/api/pyproject.toml webapp/api/.gitignore webapp/api/techgap_api webapp/api/tests
git commit -m "feat(api): scaffold core API package and database tables" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Release format and mock release

**Files:**
- Create: `webapp/api/techgap_api/release_format.py`, `webapp/api/techgap_api/mock_release.py`, `webapp/api/tests/test_release_format.py`, `webapp/api/tests/test_mock_release.py`

- [ ] **Step 1: Write the failing tests**

`webapp/api/tests/test_mock_release.py`:

```python
from techgap_api.mock_release import write_mock_release
from techgap_api.release_format import read_release


def test_mock_release_is_deterministic(tmp_path):
    a = write_mock_release(tmp_path / "a")
    b = write_mock_release(tmp_path / "b")
    files_a = sorted(p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file())
    assert files_a == files_b
    for rel in files_a:
        assert (a / rel).read_bytes() == (b / rel).read_bytes()


def test_mock_release_contains_the_edge_cases(release_dir):
    loaded = read_release(release_dir)
    bundles = {f"{ref.role_id}/{ref.cohort}": bundle for ref, bundle in loaded.bundles}

    assert bundles["data-analyst/employment"].postings == []  # role with zero assessable postings

    web = bundles["web-developer/employment"]
    assert [p.requirement_set_complete for p in web.postings] == [True, False, True]
    groups = [g for p in web.postings for g in p.groups]
    by_id = {c.component_id: c for c in web.components}
    assert any(len(g.alternatives) > 1 for g in groups)  # an OR group
    assert any(len(alt) > 1 for g in groups for alt in g.alternatives)  # an AND group
    assert any(g.requirement_unresolved for g in groups)  # insufficient job evidence
    assert any(s.status == "unresolved" for c in web.components for s in c.supports)
    assert any(c.supports == [] for c in web.components)  # supported by no course
    assert any(  # a partial case: one component supported, another not
        len(alt) > 1
        and any(by_id[i].supports for i in alt)
        and any(not by_id[i].supports for i in alt)
        for g in groups
        for alt in g.alternatives
    )

    assert any(c.cmo_knowledge_area is None for c in loaded.courses)  # unmapped course
    assert any(c.title is None for c in loaded.courses)  # title is not required
    assert {ref.pool for ref, _ in loaded.result_sets} == {"local"}  # no international set
```

`webapp/api/tests/test_release_format.py`:

```python
import hashlib
import json

import pytest

from techgap_api.release_format import ReleaseError, read_release

WEB_BUNDLE = "scoring_bundles/local-employment-web-developer.json"


def rewrite(root, rel, mutate):
    """Edit a JSON file in a release and fix its manifest hash, so only the edit under test can fail."""
    path = root / rel
    data = json.loads(path.read_bytes())
    mutate(data)
    raw = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(raw)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["sha256"][rel] = hashlib.sha256(raw).hexdigest()
    manifest_path.write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def edit_manifest(root, mutate):
    path = root / "manifest.json"
    data = json.loads(path.read_bytes())
    mutate(data)
    path.write_bytes((json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def test_reads_the_mock_release(release_dir):
    loaded = read_release(release_dir)
    assert loaded.manifest.release_id == "mock-2026-10"
    assert len(loaded.result_sets) == 3
    assert len(loaded.bundles) == 3
    assert {c.course_code for c in loaded.courses} == {"MOCK-COM1", "MOCK-WEB1", "MOCK-WEB2"}


def test_rejects_a_file_changed_after_the_manifest_was_written(release_dir):
    bundle = release_dir / WEB_BUNDLE
    bundle.write_bytes(bundle.read_bytes() + b" ")
    with pytest.raises(ReleaseError, match="sha256 mismatch"):
        read_release(release_dir)


def test_rejects_a_group_that_uses_an_unknown_component(release_dir):
    def break_it(data):
        data["postings"][0]["groups"][0]["alternatives"] = [["c-missing"]]

    rewrite(release_dir, WEB_BUNDLE, break_it)
    with pytest.raises(ReleaseError, match="unknown components"):
        read_release(release_dir)


def test_rejects_a_link_status_other_than_supported_or_unresolved(release_dir):
    def break_it(data):
        data["components"][0]["supports"][0]["status"] = "not_established"

    rewrite(release_dir, WEB_BUNDLE, break_it)
    with pytest.raises(ReleaseError, match="status"):
        read_release(release_dir)


def test_rejects_a_posting_without_title_and_company(release_dir):
    def break_it(data):
        data["job-1001-r1"]["title"] = None

    rewrite(release_dir, "evidence.json", break_it)
    with pytest.raises(ReleaseError, match="title and company"):
        read_release(release_dir)


def test_rejects_an_unsupported_format_version(release_dir):
    edit_manifest(release_dir, lambda d: d.update(format_version="9"))
    with pytest.raises(ReleaseError, match="format_version"):
        read_release(release_dir)


def test_rejects_a_file_path_outside_the_release(release_dir):
    def point_outside(data):
        data["evidence_file"] = "../outside.json"
        data["sha256"]["../outside.json"] = "0" * 64

    edit_manifest(release_dir, point_outside)
    with pytest.raises(ReleaseError, match="escapes"):
        read_release(release_dir)


def test_rejects_a_bundle_that_does_not_match_its_manifest_entry(release_dir):
    rewrite(release_dir, WEB_BUNDLE, lambda d: d.update(role_id="someone-else"))
    with pytest.raises(ReleaseError, match="does not match"):
        read_release(release_dir)
```

- [ ] **Step 2: Run to verify failure**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api/tests/test_release_format.py webapp/api/tests/test_mock_release.py -q
```

Expected: errors with `ModuleNotFoundError: No module named 'techgap_api.release_format'`.

- [ ] **Step 3: Implement `release_format.py`**

`webapp/api/techgap_api/release_format.py`:

```python
"""Release directory format v0 (DRAFT, pending the data-flow review recorded in docs/plan/RELEASE_FORMAT.md)."""
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

FORMAT_VERSION = "0"

Pool = Literal["local", "international"]
Cohort = Literal["employment", "internship"]
ScopeType = Literal["track", "role", "overall"]


class ReleaseError(Exception):
    """The release directory is missing, altered or malformed."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ResultSetRef(_Strict):
    pool: Pool
    cohort: Cohort
    scope_type: ScopeType
    scope_id: str
    window_start: str
    window_end: str
    file: str


class BundleRef(_Strict):
    pool: Pool
    cohort: Cohort
    role_id: str
    role_name: str
    file: str


class Manifest(_Strict):
    format_version: str
    release_id: str
    created_at: str
    job_cutoff: str
    syllabus_version: str
    rule_version: str
    purpose: str | None = None
    result_sets: list[ResultSetRef]
    scoring_bundles: list[BundleRef]
    evidence_file: str
    courses_file: str
    sha256: dict[str, str]

    @model_validator(mode="after")
    def _check(self):
        if self.format_version != FORMAT_VERSION:
            raise ValueError(f"unsupported format_version {self.format_version!r}")
        named = (
            {r.file for r in self.result_sets}
            | {b.file for b in self.scoring_bundles}
            | {self.evidence_file, self.courses_file}
        )
        unhashed = named - set(self.sha256)
        if unhashed:
            raise ValueError(f"files without a sha256 entry: {sorted(unhashed)}")
        return self


class Support(_Strict):
    course_code: str
    passage_ref: str
    # Contract section 3: only these two are stored; a missing link means not_established.
    status: Literal["supported", "unresolved"]


class Component(_Strict):
    component_id: str
    capability_key: str  # pending: the stable-key rule is open item P6
    supports: list[Support]


class Group(_Strict):
    group_id: str
    capability_key: str
    alternatives: list[list[str]]  # OR of ANDs of component_id
    requirement_unresolved: bool  # insufficient job evidence: unresolved for every course set


class Posting(_Strict):
    posting_id: str
    requirement_set_complete: bool
    groups: list[Group]


class ScoringBundle(_Strict):
    pool: Pool
    cohort: Cohort
    role_id: str
    role_name: str
    postings: list[Posting]
    components: list[Component]

    @model_validator(mode="after")
    def _components_exist(self):
        known = {c.component_id for c in self.components}
        for posting in self.postings:
            for group in posting.groups:
                for alternative in group.alternatives:
                    unknown = [c for c in alternative if c not in known]
                    if unknown:
                        raise ValueError(f"group {group.group_id} uses unknown components {unknown}")
        return self


class EvidenceItem(_Strict):
    kind: Literal["posting", "syllabus"]
    source_id: str
    url: str | None
    # Contract section 4: a posting shows title, company, URL and the short extracted phrase only;
    # a syllabus passage is shown in full.
    text: str
    title: str | None = None  # posting only
    company: str | None = None  # posting only
    source_field: str | None = None  # syllabus only

    @model_validator(mode="after")
    def _kind_fields(self):
        if self.kind == "posting" and not (self.title and self.company):
            raise ValueError("a posting needs title and company")
        if self.kind == "syllabus" and not self.source_field:
            raise ValueError("a syllabus passage needs source_field")
        return self


class Course(_Strict):
    course_code: str
    title: str | None
    track: str
    year_level: int | None
    semester: int | None
    extraction_status: str
    cmo_knowledge_area: str | None  # None means "unmapped"


@dataclass(frozen=True)
class LoadedRelease:
    manifest: Manifest
    result_sets: list[tuple[ResultSetRef, dict]]
    bundles: list[tuple[BundleRef, ScoringBundle]]
    evidence: dict[str, EvidenceItem]
    courses: list[Course]


def _read_verified(root: Path, manifest: Manifest, rel: str) -> bytes:
    path = (root / rel).resolve()
    if root not in path.parents:
        raise ReleaseError(f"path escapes the release directory: {rel}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ReleaseError(f"cannot read {rel}: {exc}") from exc
    if hashlib.sha256(data).hexdigest() != manifest.sha256[rel]:
        raise ReleaseError(f"sha256 mismatch for {rel}")
    return data


def read_release(root: Path) -> LoadedRelease:
    """Validate a release directory completely before anything is stored."""
    root = Path(root).resolve()
    try:
        manifest = Manifest.model_validate(json.loads((root / "manifest.json").read_bytes()))
    except FileNotFoundError as exc:
        raise ReleaseError(f"no manifest.json in {root}") from exc
    except ValueError as exc:  # bad JSON or a pydantic ValidationError
        raise ReleaseError(f"manifest.json: {exc}") from exc

    def load(rel: str):
        data = _read_verified(root, manifest, rel)
        try:
            return json.loads(data)
        except ValueError as exc:
            raise ReleaseError(f"{rel}: {exc}") from exc

    def validated(model, raw, rel: str):
        try:
            return model.model_validate(raw)
        except ValueError as exc:
            raise ReleaseError(f"{rel}: {exc}") from exc

    result_sets = []
    for ref in manifest.result_sets:
        payload = load(ref.file)
        if not isinstance(payload, dict):
            raise ReleaseError(f"{ref.file}: a result set must be a JSON object")
        result_sets.append((ref, payload))

    bundles = []
    for ref in manifest.scoring_bundles:
        bundle = validated(ScoringBundle, load(ref.file), ref.file)
        same = (bundle.pool, bundle.cohort, bundle.role_id, bundle.role_name) == (
            ref.pool,
            ref.cohort,
            ref.role_id,
            ref.role_name,
        )
        if not same:
            raise ReleaseError(f"{ref.file} does not match its manifest entry")
        bundles.append((ref, bundle))

    evidence = {
        key: validated(EvidenceItem, value, manifest.evidence_file)
        for key, value in load(manifest.evidence_file).items()
    }
    courses = [validated(Course, value, manifest.courses_file) for value in load(manifest.courses_file)]
    return LoadedRelease(manifest, result_sets, bundles, evidence, courses)
```

- [ ] **Step 4: Implement `mock_release.py`**

The mock exercises every case the contract's section 3 distinguishes. For a student whose completed set is `{MOCK-WEB1}`, job-1001's `g1` is covered, `g2` unresolved, `g6` partial; job-1003's `g3` is missing, `g4` unresolved, `g7` unresolved by flag.

`webapp/api/techgap_api/mock_release.py`:

```python
"""Deterministic mock release (format v0) to build the app against before the pipeline exists.

ponytail: hand-written fixtures, not random data; the edge cases are the point.
"""
import hashlib
import json
from pathlib import Path

from .release_format import FORMAT_VERSION

WEB_TRACK = "bsit-web-development"


def _write_json(root: Path, rel: str, value) -> bytes:
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def _support(course_code: str, passage_ref: str, status: str) -> dict:
    return {"course_code": course_code, "passage_ref": passage_ref, "status": status}


def _group(group_id: str, capability_key: str, alternatives: list, requirement_unresolved: bool = False) -> dict:
    return {
        "group_id": group_id,
        "capability_key": capability_key,
        "alternatives": alternatives,
        "requirement_unresolved": requirement_unresolved,
    }


COMPONENTS = [
    {
        "component_id": "c-html",
        "capability_key": "html-css",
        "supports": [_support("MOCK-WEB1", "syl-MOCK-WEB1-outcomes", "supported")],
    },
    {
        "component_id": "c-rest",
        "capability_key": "rest-api-design",
        "supports": [_support("MOCK-WEB1", "syl-MOCK-WEB1-outcomes", "unresolved")],
    },
    {"component_id": "c-sql", "capability_key": "sql-queries", "supports": []},
    {
        "component_id": "c-git",
        "capability_key": "version-control",
        "supports": [_support("MOCK-COM1", "syl-MOCK-COM1-outcomes", "supported")],
    },
    {
        "component_id": "c-py",
        "capability_key": "python",
        "supports": [_support("MOCK-WEB1", "syl-MOCK-WEB1-outcomes", "supported")],
    },
]

WEB_POSTINGS = [
    {
        "posting_id": "job-1001",
        "requirement_set_complete": True,
        "groups": [
            _group("g1", "html-css", [["c-html"]]),
            _group("g2", "rest-api-design", [["c-rest"]]),
            _group("g6", "sql-and-python", [["c-sql", "c-py"]]),
        ],
    },
    {"posting_id": "job-1002", "requirement_set_complete": False, "groups": []},
    {
        "posting_id": "job-1003",
        "requirement_set_complete": True,
        "groups": [
            _group("g3", "sql-queries", [["c-sql"], ["c-git"]]),
            _group("g4", "html-css", [["c-html", "c-rest"]]),
            _group("g7", "ci-cd", [], requirement_unresolved=True),
        ],
    },
]

INTERNSHIP_POSTINGS = [
    {
        "posting_id": "job-2001",
        "requirement_set_complete": True,
        "groups": [_group("g5", "html-css", [["c-html"]])],
    }
]

EVIDENCE = {
    "job-1001-r1": {
        "kind": "posting",
        "source_id": "jobstreet:ph:1001",
        "url": "https://ph.jobstreet.com/job/1001",
        "title": "Web Developer",
        "company": "Mock Co",
        "text": "responsive pages with HTML and CSS",
    },
    "syl-MOCK-WEB1-outcomes": {
        "kind": "syllabus",
        "source_id": "MOCK-WEB1",
        "url": None,
        "source_field": "course_learning_outcomes",
        "text": "Create web pages using HTML and CSS.",
    },
    "syl-MOCK-COM1-outcomes": {
        "kind": "syllabus",
        "source_id": "MOCK-COM1",
        "url": None,
        "source_field": "course_learning_outcomes",
        "text": "Use version control for a small project.",
    },
}

COURSES = [
    {
        "course_code": "MOCK-COM1",
        "title": "Mock Common Course",
        "track": "Common (IT & CS)",
        "year_level": 1,
        "semester": 1,
        "extraction_status": "ok",
        "cmo_knowledge_area": "mock-knowledge-area",
    },
    {
        "course_code": "MOCK-WEB1",
        "title": "Mock Web Lab",
        "track": "IT - Web Development",
        "year_level": 3,
        "semester": 1,
        "extraction_status": "ok",
        "cmo_knowledge_area": "mock-knowledge-area",
    },
    {
        "course_code": "MOCK-WEB2",
        "title": None,
        "track": "IT - Web Development",
        "year_level": 3,
        "semester": 2,
        "extraction_status": "needs_review",
        "cmo_knowledge_area": None,
    },
]


def _web_payload() -> dict:
    return {
        "counts": {"relevant": 3, "assessable": 2, "total": 3},
        "demand_ranking": [
            {"capability_key": "html-css", "n": 2, "N": 2},
            {"capability_key": "rest-api-design", "n": 1, "N": 2},
            {"capability_key": "sql-queries", "n": 1, "N": 2},
        ],
    }


def write_mock_release(root: Path, release_id: str = "mock-2026-10") -> Path:
    root = Path(root)
    window = {"window_start": "2025-11-01", "window_end": "2026-10-27"}
    hashes: dict[str, str] = {}
    result_refs: list[dict] = []
    bundle_refs: list[dict] = []

    def put(rel: str, value) -> None:
        hashes[rel] = hashlib.sha256(_write_json(root, rel, value)).hexdigest()

    def add_result_set(cohort: str, scope_type: str, scope_id: str, payload: dict) -> None:
        rel = f"result_sets/local-{cohort}-{scope_type}-{scope_id}.json"
        put(rel, payload)
        result_refs.append(
            {"pool": "local", "cohort": cohort, "scope_type": scope_type, "scope_id": scope_id, "file": rel, **window}
        )

    def add_bundle(cohort: str, role_id: str, role_name: str, postings: list, components: list) -> None:
        rel = f"scoring_bundles/local-{cohort}-{role_id}.json"
        put(
            rel,
            {
                "pool": "local",
                "cohort": cohort,
                "role_id": role_id,
                "role_name": role_name,
                "postings": postings,
                "components": components,
            },
        )
        bundle_refs.append(
            {"pool": "local", "cohort": cohort, "role_id": role_id, "role_name": role_name, "file": rel}
        )

    add_result_set("employment", "track", WEB_TRACK, _web_payload())
    add_result_set("employment", "role", "web-developer", _web_payload())
    add_result_set(
        "internship",
        "track",
        WEB_TRACK,
        {
            "counts": {"relevant": 1, "assessable": 1, "total": 1},
            "demand_ranking": [{"capability_key": "html-css", "n": 1, "N": 1}],
        },
    )
    add_bundle("employment", "web-developer", "Web Developer", WEB_POSTINGS, COMPONENTS)
    add_bundle("employment", "data-analyst", "Data Analyst", [], [])  # a role with no assessable postings
    add_bundle("internship", "web-developer", "Web Developer", INTERNSHIP_POSTINGS, COMPONENTS[:1])
    put("evidence.json", EVIDENCE)
    put("courses.json", COURSES)

    manifest = {
        "format_version": FORMAT_VERSION,
        "release_id": release_id,
        "created_at": "2026-10-31T00:00:00Z",
        "job_cutoff": "2026-10-27T00:00:00Z",
        "syllabus_version": "mock-syl-1",
        "rule_version": "mock-rules-0",
        "purpose": "mock",
        "result_sets": result_refs,
        "scoring_bundles": bundle_refs,
        "evidence_file": "evidence.json",
        "courses_file": "courses.json",
        "sha256": hashes,
    }
    _write_json(root, "manifest.json", manifest)
    return root
```

- [ ] **Step 5: Run to verify pass**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Expected: `12 passed`.

- [ ] **Step 6: Commit (only when the user asks)**

```bash
git add webapp/api/techgap_api/release_format.py webapp/api/techgap_api/mock_release.py webapp/api/tests/test_release_format.py webapp/api/tests/test_mock_release.py
git commit -m "feat(api): release format v0 reader and deterministic mock release" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Loader and active-release pointer

**Files:**
- Create: `webapp/api/techgap_api/loader.py`, `webapp/api/tests/test_loader.py`

- [ ] **Step 1: Write the failing tests**

`webapp/api/tests/test_loader.py`:

```python
import pytest
from sqlalchemy import func, select

from techgap_api.db import evidence, release_courses, releases, result_sets, scoring_bundles
from techgap_api.loader import activate_release, active_release_id, load_release
from techgap_api.mock_release import write_mock_release
from techgap_api.release_format import ReleaseError


def count(engine, table):
    with engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(table)).scalar_one()


def test_load_inserts_every_part(engine, release_dir):
    assert load_release(engine, release_dir) == "mock-2026-10"
    assert count(engine, releases) == 1
    assert count(engine, result_sets) == 3
    assert count(engine, scoring_bundles) == 3
    assert count(engine, evidence) == 3
    assert count(engine, release_courses) == 3


def test_load_twice_is_refused(engine, release_dir):
    load_release(engine, release_dir)
    with pytest.raises(ReleaseError, match="already loaded"):
        load_release(engine, release_dir)
    assert count(engine, releases) == 1


def test_a_tampered_release_is_not_loaded(engine, release_dir):
    bundle = release_dir / "scoring_bundles" / "local-employment-web-developer.json"
    bundle.write_bytes(bundle.read_bytes() + b" ")
    with pytest.raises(ReleaseError, match="sha256 mismatch"):
        load_release(engine, release_dir)
    assert count(engine, releases) == 0


def test_activate_moves_the_pointer(engine, release_dir, tmp_path):
    load_release(engine, release_dir)
    load_release(engine, write_mock_release(tmp_path / "second", release_id="mock-2026-11"))

    activate_release(engine, "mock-2026-10")
    with engine.connect() as conn:
        assert active_release_id(conn) == "mock-2026-10"

    activate_release(engine, "mock-2026-11")
    with engine.connect() as conn:
        assert active_release_id(conn) == "mock-2026-11"


def test_activating_an_unknown_release_is_refused(engine):
    with pytest.raises(ReleaseError, match="not a ready release"):
        activate_release(engine, "nope")
```

- [ ] **Step 2: Run to verify failure**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api/tests/test_loader.py -q
```

Expected: error `ModuleNotFoundError: No module named 'techgap_api.loader'`.

- [ ] **Step 3: Implement `loader.py`**

`webapp/api/techgap_api/loader.py`:

```python
"""Import a validated release directory and move the active-release pointer."""
from pathlib import Path

from sqlalchemy import insert, select, update
from sqlalchemy.engine import Connection, Engine

from .db import app_state, evidence, release_courses, releases, result_sets, scoring_bundles
from .release_format import ReleaseError, read_release


def _insert_all(conn: Connection, table, rows: list[dict]) -> None:
    if rows:
        conn.execute(insert(table), rows)


def load_release(engine: Engine, root: Path) -> str:
    """Insert a release in one transaction; any failure leaves the database unchanged."""
    loaded = read_release(root)
    manifest = loaded.manifest
    release_id = manifest.release_id
    with engine.begin() as conn:
        exists = conn.execute(select(releases.c.release_id).where(releases.c.release_id == release_id)).first()
        if exists:
            raise ReleaseError(f"release already loaded: {release_id}")
        conn.execute(
            insert(releases).values(
                release_id=release_id,
                created_at=manifest.created_at,
                job_cutoff=manifest.job_cutoff,
                syllabus_version=manifest.syllabus_version,
                rule_version=manifest.rule_version,
                purpose=manifest.purpose,
                status="ready",
                manifest=manifest.model_dump(mode="json"),
            )
        )
        _insert_all(
            conn,
            result_sets,
            [
                {
                    "release_id": release_id,
                    "pool": ref.pool,
                    "cohort": ref.cohort,
                    "scope_type": ref.scope_type,
                    "scope_id": ref.scope_id,
                    "window_start": ref.window_start,
                    "window_end": ref.window_end,
                    "payload": payload,
                }
                for ref, payload in loaded.result_sets
            ],
        )
        _insert_all(
            conn,
            scoring_bundles,
            [
                {
                    "release_id": release_id,
                    "pool": ref.pool,
                    "cohort": ref.cohort,
                    "role_id": ref.role_id,
                    "role_name": ref.role_name,
                    "payload": bundle.model_dump(mode="json"),
                }
                for ref, bundle in loaded.bundles
            ],
        )
        _insert_all(
            conn,
            evidence,
            [
                {
                    "release_id": release_id,
                    "ref": key,
                    "kind": item.kind,
                    "source_id": item.source_id,
                    "url": item.url,
                    "title": item.title,
                    "company": item.company,
                    "source_field": item.source_field,
                    "text": item.text,
                }
                for key, item in loaded.evidence.items()
            ],
        )
        _insert_all(
            conn,
            release_courses,
            [
                {"release_id": release_id, "course_code": c.course_code, "payload": c.model_dump(mode="json")}
                for c in loaded.courses
            ],
        )
    return release_id


def active_release_id(conn: Connection) -> str | None:
    return conn.execute(select(app_state.c.active_release_id).where(app_state.c.id == 1)).scalar_one_or_none()


def activate_release(engine: Engine, release_id: str) -> None:
    """Make a ready release the one the app serves by default. This is also how a developer rolls back."""
    with engine.begin() as conn:
        status = conn.execute(select(releases.c.status).where(releases.c.release_id == release_id)).scalar_one_or_none()
        if status != "ready":
            raise ReleaseError(f"not a ready release: {release_id}")
        moved = conn.execute(
            update(app_state).where(app_state.c.id == 1).values(active_release_id=release_id)
        ).rowcount
        if not moved:
            conn.execute(insert(app_state).values(id=1, active_release_id=release_id))
```

- [ ] **Step 4: Run to verify pass**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Expected: `17 passed`.

- [ ] **Step 5: Commit (only when the user asks)**

```bash
git add webapp/api/techgap_api/loader.py webapp/api/tests/test_loader.py
git commit -m "feat(api): release loader and active-release pointer" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Public read API

**Files:**
- Create: `webapp/api/techgap_api/app.py`, `webapp/api/tests/test_api.py`

- [ ] **Step 1: Write the failing tests**

`webapp/api/tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient

from techgap_api.app import create_app
from techgap_api.loader import activate_release, load_release


@pytest.fixture
def client(engine, release_dir):
    load_release(engine, release_dir)
    activate_release(engine, "mock-2026-10")
    return TestClient(create_app(engine))


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_lists_releases_with_the_active_flag(client):
    body = client.get("/releases").json()
    assert [(r["release_id"], r["active"], r["purpose"]) for r in body] == [("mock-2026-10", True, "mock")]


def test_meta_lists_pools_roles_and_courses(client):
    meta = client.get("/releases/mock-2026-10/meta").json()
    assert meta["syllabus_version"] == "mock-syl-1"
    assert meta["pools"] == {"local": ["employment", "internship"]}
    assert {(r["role_id"], r["role_name"], r["cohort"]) for r in meta["roles"]} == {
        ("web-developer", "Web Developer", "employment"),
        ("data-analyst", "Data Analyst", "employment"),
        ("web-developer", "Web Developer", "internship"),
    }
    assert [c["course_code"] for c in meta["courses"]] == ["MOCK-COM1", "MOCK-WEB1", "MOCK-WEB2"]


def test_result_sets_can_be_filtered(client):
    url = "/releases/mock-2026-10/result-sets"
    assert len(client.get(url).json()) == 3

    internship = client.get(url, params={"cohort": "internship"}).json()
    assert [r["scope_id"] for r in internship] == ["bsit-web-development"]
    assert internship[0]["window_end"] == "2026-10-27"

    assert client.get(url, params={"pool": "international"}).json() == []  # absent pool has no result set
    assert client.get(url, params={"pool": "nope"}).status_code == 422


def test_evidence_shows_a_posting_as_title_company_url_and_phrase_only(client):
    job = client.get("/releases/mock-2026-10/evidence/job-1001-r1").json()
    assert job["kind"] == "posting"
    assert (job["title"], job["company"]) == ("Web Developer", "Mock Co")
    assert job["url"] == "https://ph.jobstreet.com/job/1001"
    assert job["text"] == "responsive pages with HTML and CSS"

    syllabus = client.get("/releases/mock-2026-10/evidence/syl-MOCK-WEB1-outcomes").json()
    assert syllabus["source_field"] == "course_learning_outcomes"

    assert client.get("/releases/mock-2026-10/evidence/missing").status_code == 404


def test_unknown_release_is_404(client):
    assert client.get("/releases/nope/meta").status_code == 404
    assert client.get("/releases/nope/result-sets").status_code == 404
```

- [ ] **Step 2: Run to verify failure**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api/tests/test_api.py -q
```

Expected: error `ModuleNotFoundError: No module named 'techgap_api.app'`.

- [ ] **Step 3: Implement `app.py`**

`webapp/api/techgap_api/app.py`:

```python
"""Public read-only API. Results are displayed as the release stores them; nothing is recomputed here."""
from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.engine import Connection, Engine

from .db import evidence, release_courses, releases, result_sets, scoring_bundles
from .loader import active_release_id
from .release_format import Cohort, Pool, ScopeType

RELEASE_FIELDS = ("release_id", "created_at", "job_cutoff", "syllabus_version", "rule_version", "purpose")
RESULT_SET_FIELDS = ("pool", "cohort", "scope_type", "scope_id", "window_start", "window_end", "payload")
EVIDENCE_FIELDS = ("ref", "kind", "source_id", "url", "title", "company", "source_field", "text")


def _ready_release(conn: Connection, release_id: str):
    row = conn.execute(
        select(releases).where(releases.c.release_id == release_id, releases.c.status == "ready")
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"unknown release: {release_id}")
    return row


def create_app(engine: Engine) -> FastAPI:
    app = FastAPI(title="TechGap API")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/releases")
    def list_releases():
        with engine.connect() as conn:
            active = active_release_id(conn)
            rows = conn.execute(
                select(releases)
                .where(releases.c.status == "ready")
                .order_by(releases.c.created_at.desc(), releases.c.release_id.desc())
            ).mappings().all()
        return [{**{k: row[k] for k in RELEASE_FIELDS}, "active": row["release_id"] == active} for row in rows]

    @app.get("/releases/{release_id}/meta")
    def release_meta(release_id: str):
        with engine.connect() as conn:
            row = _ready_release(conn, release_id)
            sets = conn.execute(
                select(result_sets.c.pool, result_sets.c.cohort).where(result_sets.c.release_id == release_id)
            ).all()
            bundles = conn.execute(
                select(
                    scoring_bundles.c.pool,
                    scoring_bundles.c.cohort,
                    scoring_bundles.c.role_id,
                    scoring_bundles.c.role_name,
                ).where(scoring_bundles.c.release_id == release_id)
            ).all()
            courses = [
                r.payload
                for r in conn.execute(
                    select(release_courses.c.payload)
                    .where(release_courses.c.release_id == release_id)
                    .order_by(release_courses.c.course_code)
                )
            ]
        pools: dict[str, set[str]] = {}
        for pool, cohort, *_ in [*sets, *bundles]:
            pools.setdefault(pool, set()).add(cohort)
        return {
            **{k: row[k] for k in RELEASE_FIELDS},
            "pools": {pool: sorted(cohorts) for pool, cohorts in sorted(pools.items())},
            "roles": sorted(
                (
                    {"pool": p, "cohort": c, "role_id": r, "role_name": n}
                    for p, c, r, n in bundles
                ),
                key=lambda x: (x["pool"], x["cohort"], x["role_name"]),
            ),
            "courses": courses,
        }

    @app.get("/releases/{release_id}/result-sets")
    def get_result_sets(
        release_id: str,
        pool: Pool | None = None,
        cohort: Cohort | None = None,
        scope_type: ScopeType | None = None,
        scope_id: str | None = None,
    ):
        filters = {"pool": pool, "cohort": cohort, "scope_type": scope_type, "scope_id": scope_id}
        with engine.connect() as conn:
            _ready_release(conn, release_id)
            query = select(result_sets).where(result_sets.c.release_id == release_id)
            for column, value in filters.items():
                if value is not None:
                    query = query.where(result_sets.c[column] == value)
            rows = conn.execute(query.order_by(result_sets.c.id)).mappings().all()
        return [{k: row[k] for k in RESULT_SET_FIELDS} for row in rows]

    @app.get("/releases/{release_id}/evidence/{ref}")
    def get_evidence(release_id: str, ref: str):
        with engine.connect() as conn:
            _ready_release(conn, release_id)
            row = conn.execute(
                select(evidence).where(evidence.c.release_id == release_id, evidence.c.ref == ref)
            ).mappings().first()
        if row is None:
            raise HTTPException(status_code=404, detail=f"unknown evidence: {ref}")
        return {k: row[k] for k in EVIDENCE_FIELDS}

    return app
```

- [ ] **Step 4: Run to verify pass**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Expected: `23 passed`.

- [ ] **Step 5: Commit (only when the user asks)**

```bash
git add webapp/api/techgap_api/app.py webapp/api/tests/test_api.py
git commit -m "feat(api): public read endpoints for releases, result sets and evidence" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Developer CLI and entry point

**Files:**
- Create: `webapp/api/techgap_api/cli.py`, `webapp/api/techgap_api/main.py`, `webapp/api/tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

`webapp/api/tests/test_cli.py`:

```python
from techgap_api.cli import main


def test_mock_load_activate_round_trip(engine, tmp_path, capsys):
    target = tmp_path / "rel"
    assert main(["mock", str(target)], engine=engine) == 0
    assert main(["load", str(target)], engine=engine) == 0
    assert main(["activate", "mock-2026-10"], engine=engine) == 0
    assert "activated mock-2026-10" in capsys.readouterr().out


def test_a_bad_release_returns_exit_code_1(engine, tmp_path, capsys):
    assert main(["load", str(tmp_path / "missing")], engine=engine) == 1
    assert "error:" in capsys.readouterr().err
```

- [ ] **Step 2: Run to verify failure**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api/tests/test_cli.py -q
```

Expected: error `ModuleNotFoundError: No module named 'techgap_api.cli'`.

- [ ] **Step 3: Implement the CLI and the entry point**

`webapp/api/techgap_api/cli.py`:

```python
"""Developer commands: write a mock release, load a release directory, activate (or roll back to) a release."""
import argparse
import sys
from pathlib import Path

from .db import engine_from_env, init_db
from .loader import activate_release, load_release
from .mock_release import write_mock_release
from .release_format import ReleaseError


def main(argv=None, engine=None) -> int:
    parser = argparse.ArgumentParser(prog="techgap-api")
    commands = parser.add_subparsers(dest="command", required=True)
    mock = commands.add_parser("mock", help="write a deterministic mock release")
    mock.add_argument("directory", type=Path)
    mock.add_argument("--release-id", default="mock-2026-10")
    load = commands.add_parser("load", help="validate and import a release directory")
    load.add_argument("directory", type=Path)
    activate = commands.add_parser("activate", help="make a loaded release the active one")
    activate.add_argument("release_id")
    args = parser.parse_args(argv)

    if args.command == "mock":
        write_mock_release(args.directory, args.release_id)
        print(f"wrote mock release {args.release_id} to {args.directory}")
        return 0

    engine = engine or engine_from_env()
    init_db(engine)
    try:
        if args.command == "load":
            print(f"loaded {load_release(engine, args.directory)}")
        else:
            activate_release(engine, args.release_id)
            print(f"activated {args.release_id}")
    except ReleaseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`webapp/api/techgap_api/main.py`:

```python
"""Uvicorn entry point: `uvicorn techgap_api.main:app`. Reads DATABASE_URL (default: local SQLite file)."""
from .app import create_app
from .db import engine_from_env, init_db

engine = engine_from_env()
init_db(engine)
app = create_app(engine)
```

- [ ] **Step 4: Run to verify pass**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Expected: `25 passed`.

- [ ] **Step 5: Commit (only when the user asks)**

```bash
git add webapp/api/techgap_api/cli.py webapp/api/techgap_api/main.py webapp/api/tests/test_cli.py
git commit -m "feat(api): developer CLI and uvicorn entry point" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Release-format document for the pipeline session

**Files:**
- Create: `docs/plan/RELEASE_FORMAT.md`

This is the interface document the data-flow session reviews (open item P9). It describes what the models in `release_format.py` already enforce. It does not change `PLANNED_DATA_FLOW.md`.

- [ ] **Step 1: Write the document**

`docs/plan/RELEASE_FORMAT.md`:

```markdown
# TechGap result release format — v0 DRAFT

**Status:** Draft by the frontend/backend session, 2026-10-31. Not yet reviewed by the data-flow session; nothing here changes the meaning of any result in [PLANNED_DATA_FLOW.md](PLANNED_DATA_FLOW.md), which wins on any disagreement. The enforced shape is `webapp/api/techgap_api/release_format.py`; a deterministic example is written by `python -m techgap_api.cli mock <dir>`.

**Purpose:** the only interface between the pipeline and the web app. One immutable directory per refresh. The app imports it whole or not at all.

## Files

| Path | Content |
| --- | --- |
| `manifest.json` | `format_version` (`"0"`), `release_id`, `created_at`, `job_cutoff`, `syllabus_version`, `rule_version`, optional `purpose` (free text), the list of result sets and scoring bundles, `evidence_file`, `courses_file`, and `sha256` for every file the manifest names |
| `result_sets/*.json` | One JSON object per result set. Keys of the set (in the manifest): `pool` (`local`/`international`), `cohort` (`employment`/`internship`), `scope_type` (`track`/`role`/`overall`), `scope_id`, `window_start`, `window_end`. A pool with no releasable data has no result set. The payload shape is free-form in v0 |
| `scoring_bundles/*.json` | Per pool, cohort and role (`role_id`, `role_name`): `postings[]` (`posting_id`, `requirement_set_complete`, `groups[]`) and `components[]`. A group has `group_id`, `capability_key`, `requirement_unresolved` and `alternatives`: a list of alternatives, each a list of `component_id` (OR of ANDs). A component has `component_id`, `capability_key` and `supports[]` (`course_code`, `passage_ref`, `status` = `supported` or `unresolved`). A missing link means `not_established` and is not stored (contract section 3) |
| `evidence.json` | Map from a url-safe reference to an item. Posting: `kind`, `source_id`, `url`, `title`, `company`, `text` = the short extracted requirement phrase only. Syllabus passage: `kind`, `source_id` (course code), `source_field`, `text` = the full passage (contract section 4) |
| `courses.json` | List of `course_code`, `title` (nullable), `track` (the syllabus JSON value), `year_level`, `semester`, `extraction_status`, `cmo_knowledge_area` (null means "unmapped") |
| `failure.json` | Written instead of a release on failure (entry-command decision D7); not read by the loader |

## What the app does with it

- Verifies every hash and path, then imports in one transaction. An invalid release is never partly imported.
- Serves result sets as stored.
- Student scoring applies the contract's section 3 rules to the scoring bundles: component status for a course set, alternative and group status, `requirement_unresolved`, posting coverage, scored / qualified / not scored, bounds and the unweighted mean; section 5 ranking, roadmap and "possible later".
- Never reads a file that is not named in the manifest.

## Decided in the contract (2026-10-31), reflected above

P1 (group status), P2 (bounds), P3 (combined alignment), P4 (ranking), P5 (roadmap gaps, "possible later"), P7 (Review list: ascending `n/N`, no cutoff, CHED-mandated flag), P8 (public display of a job: title, company, URL, extracted phrase).

## Pending (open for the data-flow session)

| Item | Field affected |
| --- | --- |
| P6 | How `capability_key` is formed and kept stable across releases (learning resources are keyed by it) |
| P9 | Review of this document against what the pipeline can supply |
| Payloads | The exact shape of faculty and Review-list result-set payloads (section 4 outputs) is not fixed in v0 |
```

- [ ] **Step 2: Commit (only when the user asks)**

```bash
git add docs/plan/RELEASE_FORMAT.md
git commit -m "docs(plan): draft release format v0 for pipeline review" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 7: End-to-end smoke run

**Files:**
- Create: `webapp/api/README.md`

- [ ] **Step 1: Write the short README**

`webapp/api/README.md`:

````markdown
# TechGap API

```bash
py -3.13 -m venv webapp/api/.venv
webapp/api/.venv/Scripts/python -m pip install -e "webapp/api[dev]"
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Local run against a SQLite file (`DATABASE_URL` selects Postgres instead):

```bash
cd webapp/api
.venv/Scripts/python -m techgap_api.cli mock ../../.tmp-mock-release
.venv/Scripts/python -m techgap_api.cli load ../../.tmp-mock-release
.venv/Scripts/python -m techgap_api.cli activate mock-2026-10
.venv/Scripts/python -m uvicorn techgap_api.main:app --port 8000
```

`activate` is also how a developer rolls back to an earlier release.
````

- [ ] **Step 2: Run the full suite**

```bash
webapp/api/.venv/Scripts/python -m pytest webapp/api -q
```

Expected: `25 passed`.

- [ ] **Step 3: Run the real server once against the mock release**

```bash
cd webapp/api
.venv/Scripts/python -m techgap_api.cli mock ../../.tmp-mock-release
.venv/Scripts/python -m techgap_api.cli load ../../.tmp-mock-release
.venv/Scripts/python -m techgap_api.cli activate mock-2026-10
.venv/Scripts/python -m uvicorn techgap_api.main:app --port 8000
```

Run the last command in the background. Expected CLI output: `wrote mock release ...`, `loaded mock-2026-10`, `activated mock-2026-10`.

- [ ] **Step 4: Check the endpoints**

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/releases
curl -s "http://127.0.0.1:8000/releases/mock-2026-10/result-sets?cohort=internship"
curl -s http://127.0.0.1:8000/releases/mock-2026-10/evidence/job-1001-r1
```

Expected: `{"status":"ok"}`; a one-element list with `"active":true`; one result set for `bsit-web-development`; an evidence item with `title`, `company`, `url` and the short phrase. Stop the server.

- [ ] **Step 5: Remove the temporary files**

```bash
cd ../..
rm -rf .tmp-mock-release webapp/api/techgap.db
git status --short webapp docs/plan/RELEASE_FORMAT.md
```

Expected: only the files created by this plan are listed (the repo's older uncommitted changes appear elsewhere and stay untouched).

- [ ] **Step 6: Commit (only when the user asks)**

```bash
git add webapp/api/README.md
git commit -m "docs(api): add run instructions" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

## Self-review (against the spec and the 2026-10-31 contract)

| Spec or contract item | Covered by |
| --- | --- |
| Postgres tables `releases`, `app_state`, `result_sets`, `scoring_bundles`, `evidence`, courses | Task 1 |
| Immutable release, hash-verified, imported in one transaction | Tasks 2 and 3 |
| Active-release pointer; developer rollback | Task 3, CLI in Task 5 |
| Public read endpoints; `n/N` and window stored per result set; absent pool has no set | Task 4 |
| Contract §3: only `supported`/`unresolved` links stored; `requirement_unresolved` | Task 2 (format, mock, tests) |
| Contract §4: job shown as title, company, URL, phrase; syllabus passage in full | Tasks 1, 2, 3, 4 |
| Contract §5: role name needed for tie ordering | Tasks 1–4 (`role_name`) |
| Mock first, with every status case | Task 2 |
| Release-format document for the pipeline session | Task 6 |
| `syllabus_versions`, `jobs`, `learning_resources`, buckets, retention | Not here: plan C |
| Student scoring and endpoints | Not here: plan D (rules decided; needs this plan first) |
| Auth, upload, workflow dispatch | Not here: plan C |
| Frontend | Not here: plan B |

Names used across tasks match: `read_release`, `write_mock_release`, `load_release`, `activate_release`, `active_release_id`, `create_app`, `main`, `normalize_database_url`, `engine_from_env`, `init_db`. Test counts per stage: 2, 12, 17, 23, 25. The code has not been executed; the first run of Task 1 Step 7 onward is its first verification, and the unpinned dependency ranges in `pyproject.toml` have not been checked against the package index.
