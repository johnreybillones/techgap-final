"""Durable local acquisition checkpoints and serial budget accounting."""
import json
import os
import re
import uuid
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path


class StateError(RuntimeError):
    pass


ACTIVE = {"reserved", "start_outcome_unknown", "running", "downloading", "downloaded", "importing"}


def _process_alive(pid):
    if os.name == "nt":
        # ponytail: os.kill(pid, 0) can signal a Windows process; query its handle instead.
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87  # Only invalid PID proves a stale lock.
        try:
            status = wintypes.DWORD()
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(status)) or status.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    tmp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(path))


class AcquisitionState:
    def __init__(self, campaign_root):
        self.root = Path(campaign_root)
        self.requests = self.root / "requests"
        self.requests.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.root / "budget_ledger.jsonl"
        self.lock_path = self.root / ".acquisition.lock"
        self._repair_ledger()

    def _repair_ledger(self):
        if not self.ledger_path.exists(): return
        lines = self.ledger_path.read_text(encoding="utf-8").splitlines()
        valid = []
        for line in lines:
            try:
                json.loads(line)
                valid.append(line)
            except json.JSONDecodeError:
                break
        if len(valid) != len(lines):
            tmp = self.ledger_path.with_suffix(".jsonl.tmp")
            tmp.write_text("".join(line + "\n" for line in valid), encoding="utf-8")
            os.replace(str(tmp), str(self.ledger_path))

    def _ledger(self):
        self._repair_ledger()
        if not self.ledger_path.exists(): return []
        return [json.loads(row) for row in self.ledger_path.read_text(encoding="utf-8").splitlines() if row]

    def _append_event(self, row):
        rows = self._ledger()
        key = row.get("event_id")
        if key and any(old.get("event_id") == key for old in rows): return
        with self.ledger_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    def _path(self, request_id):
        if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", request_id):
            raise StateError("invalid_request_id")
        return self.requests / (request_id + ".json")

    def get(self, request_id):
        path = self._path(request_id)
        if not path.exists(): raise StateError("unknown_request_id")
        return json.loads(path.read_text(encoding="utf-8"))

    def update(self, request_id, status, **fields):
        record = self.get(request_id)
        record.update(fields)
        record["status"] = status
        record["updated_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        atomic_json(self._path(request_id), record)
        return record

    def reserve(self, request):
        request_id = request["request_id"]
        path = self._path(request_id)
        if path.exists():
            existing = self.get(request_id)
            if existing.get("config_sha256") != request.get("config_sha256") or existing.get("input") != request.get("input"):
                raise StateError("request_id_conflict")
            return existing
        if any(row.get("status") in ACTIVE or row.get("billing_status") in {"reserved", "unknown"}
               for row in self._all_requests()):
            raise StateError("unresolved_acquisition_blocks_new_start")
        if any(row.get("cap_violation") for row in self._all_requests()):
            raise StateError("prior_run_exceeded_pilot_cap")
        ledger = self._ledger()
        settled = {r.get("request_id") for r in ledger if r.get("event") in {"settlement", "release"}}
        outstanding = sum((Decimal(r["amount_usd"]) for r in ledger if r.get("event") == "reservation"
                           and r.get("request_id") not in settled), Decimal("0"))
        config = json.loads((self.root / "collection_config.json").read_text(encoding="utf-8")) if (self.root / "collection_config.json").exists() else {}
        adapter = config.get("live_adapter", {})
        ceiling = Decimal(str(adapter.get("campaign_ceiling_usd", "0")))
        baseline = Decimal(str(adapter.get("baseline_spend_usd", "0")))
        charges = sum((Decimal(r["amount_usd"]) for r in ledger if r.get("event") == "settlement"), Decimal("0"))
        requested = Decimal(str(request["reserved_usd"]))
        if requested <= 0 or requested > Decimal("0.05") or ceiling > Decimal("0.30") or int(request.get("input", {}).get("results_wanted", 0)) > 25:
            raise StateError("pilot_run_or_campaign_cap_exceeded")
        requests = self._all_requests()
        live_config = config.get("live_collection_enabled") is True
        core_ids = config.get("pilot_core_query_ids", [])
        conditional = config.get("pilot_optional_query_ids", [])
        maximum_starts = 8
        if live_config:
            queries = config.get("queries") or []
            query_rows = {row.get("query_id"): row for row in queries if isinstance(row, dict)}
            configured_ids = set(query_rows)
            valid_core_list = (isinstance(queries, list) and len(query_rows) == len(queries) and
                               isinstance(core_ids, list) and
                               all(isinstance(qid, str) for qid in core_ids) and
                               len(set(core_ids)) == len(core_ids) and set(core_ids) <= configured_ids)
            if not valid_core_list:
                raise StateError("pilot_core_query_scope_invalid")
            if len(core_ids) == 4:
                if conditional != []:
                    raise StateError("pilot_four_game_mode_has_no_optional_queries")
                core_rows = [query_rows[qid] for qid in core_ids]
                if any(row.get("family") != "Game Development" or row.get("status", "enabled") != "enabled"
                       for row in core_rows):
                    raise StateError("pilot_four_core_queries_must_be_game_development_only")
            elif len(core_ids) == 6:
                if [query_rows[qid].get("family") for qid in core_ids[:5]] != [
                        "Intelligent Systems", "Game Development", "Network Technology", "Web Development", "Shared/core"]:
                    raise StateError("pilot_core_queries_must_cover_four_tracks_and_shared_work")
                if any(query_rows[qid].get("status", "enabled") != "enabled" for qid in core_ids):
                    raise StateError("pilot_core_queries_must_be_enabled")
            else:
                raise StateError("pilot_requires_six_core_or_four_game_queries")
            if (not isinstance(conditional, list) or len(conditional) > 2 or
                    any(not isinstance(qid, str) for qid in conditional) or
                    len(set(conditional)) != len(conditional) or
                    not set(conditional) <= configured_ids or set(conditional) & set(core_ids)):
                raise StateError("invalid_conditional_query_scope")
            if any(query_rows[qid].get("status", "enabled") != "enabled" for qid in conditional):
                raise StateError("conditional_queries_must_be_enabled")
            maximum_starts = len(core_ids) + len(conditional)
        if len(requests) >= maximum_starts:
            raise StateError("pilot_start_limit_reached")
        if live_config and (ceiling <= 0 or Decimal(str(adapter.get("baseline_spend_usd", 0))) < 0
                or ceiling - Decimal(str(adapter.get("baseline_spend_usd", 0))) > Decimal("0.30")):
            raise StateError("pilot_campaign_cap_invalid")
        options = request.get("run_options", {})
        if live_config and (options.get("maxTotalChargeUsd", float(requested)) > float(requested)
                or options.get("timeout") != 300 or options.get("restartOnError") is not False):
            raise StateError("pilot_run_options_exceed_safety_limits")
        if request.get("query_id") is not None and any(row.get("query_id") == request.get("query_id") for row in requests):
            raise StateError("pilot_query_already_started")
        if live_config and request.get("query_id") not in core_ids:
            evidence = (config.get("conditional_start_evidence") or {}).get(request.get("query_id"))
            settled_core = {row.get("query_id") for row in requests
                if row.get("query_id") in core_ids and row.get("status") in {"imported", "failed"}
                and row.get("billing_status") == "reconciled"}
            if (request.get("query_id") not in conditional or not isinstance(evidence, dict)
                    or not evidence.get("observed_gap") or not evidence.get("comparison_rule")
                    or settled_core != set(core_ids)):
                raise StateError("conditional_start_requires_reviewed_core_gap_and_evidence")
        if ceiling and requested > ceiling - baseline - charges - outstanding:
            raise StateError("insufficient_unreserved_campaign_funds")
        record = dict(request, status="reserved", billing_status="reserved")
        atomic_json(path, record)
        self._append_event({"event": "reservation", "event_id": "reservation:" + request_id,
                            "request_id": request_id, "amount_usd": str(requested)})
        return record

    def _all_requests(self):
        return [json.loads(p.read_text(encoding="utf-8")) for p in self.requests.glob("*.json")]

    def settle(self, request_id, run_id, amount_usd, *, evidence=None):
        amount = Decimal(str(amount_usd))
        if not amount.is_finite() or amount < 0: raise StateError("invalid_settlement_amount")
        request = self.get(request_id)
        if request.get("run_id") and request.get("run_id") != run_id:
            raise StateError("settlement_run_id_mismatch")
        event_id = "settlement:" + run_id
        self._append_event({"event": "settlement", "event_id": event_id, "request_id": request_id,
                            "run_id": run_id, "amount_usd": str(amount), "evidence": evidence or {}})
        config = json.loads((self.root / "collection_config.json").read_text(encoding="utf-8")) if (self.root / "collection_config.json").exists() else {}
        adapter = config.get("live_adapter", {})
        cap_violation = amount > Decimal(str(request.get("reserved_usd", "0.05")))
        if config.get("live_collection_enabled") is True:
            ceiling = Decimal(str(adapter.get("campaign_ceiling_usd", "0")))
            baseline = Decimal(str(adapter.get("baseline_spend_usd", "0")))
            settled = sum((Decimal(row["amount_usd"]) for row in self._ledger() if row.get("event") == "settlement"), Decimal("0"))
            cap_violation = cap_violation or settled > ceiling - baseline or amount > Decimal("0.05")
        settled_status = "failed" if cap_violation else request.get("status", "imported")
        self.update(request_id, settled_status, billing_status="reconciled",
                    actual_charge_usd=str(amount), cap_violation=cap_violation)
        if cap_violation:
            raise StateError("provider_charge_exceeded_pilot_cap; charge recorded and further starts blocked")

    def reconcile_no_run(self, request_id, evidence_path):
        request = self.get(request_id)
        if request.get("run_id") or request.get("status") not in {"reserved", "start_outcome_unknown"}:
            raise StateError("request_is_not_eligible_for_no_run_reconciliation")
        evidence = Path(evidence_path)
        if not evidence.is_file(): raise StateError("no_run_evidence_file_missing")
        self._append_event({"event": "release", "event_id": "release:" + request_id,
            "request_id": request_id, "amount_usd": "0", "evidence_file": str(evidence.resolve()),
            "reason": "operator_verified_no_remote_run"})
        self.update(request_id, "failed", billing_status="reconciled", reservation_released=True,
                    last_error_category="verified_no_remote_run", no_run_evidence=str(evidence.resolve()))

    def available(self, ceiling, baseline):
        rows = self._ledger()
        settled = {r.get("request_id") for r in rows if r.get("event") in {"settlement", "release"}}
        reserved = sum((Decimal(r["amount_usd"]) for r in rows if r.get("event") == "reservation" and r.get("request_id") not in settled), Decimal("0"))
        charges = sum((Decimal(r["amount_usd"]) for r in rows if r.get("event") == "settlement"), Decimal("0"))
        return str(Decimal(str(ceiling)) - Decimal(str(baseline)) - charges - reserved)

    @contextmanager
    def lock(self):
        try:
            self.lock_path.mkdir()
            (self.lock_path / "owner.json").write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")
        except FileExistsError:
            try:
                owner = json.loads((self.lock_path / "owner.json").read_text(encoding="utf-8"))
                pid = int(owner["pid"])
                if _process_alive(pid):
                    raise StateError("campaign_acquisition_lock_held")
                stale = self.lock_path.with_name(self.lock_path.name + ".stale-" + uuid.uuid4().hex)
                self.lock_path.rename(stale)
                for child in stale.iterdir(): child.unlink()
                stale.rmdir()
                self.lock_path.mkdir()
                (self.lock_path / "owner.json").write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")
            except StateError:
                raise
            except Exception as exc:
                raise StateError("campaign_lock_stale_or_corrupt; inspect saved requests before recovery") from exc
        try:
            yield
        finally:
            try:
                for path in self.lock_path.iterdir(): path.unlink()
                self.lock_path.rmdir()
            except FileNotFoundError: pass
