"""Bounded Apify adapter. Imports and previews are offline; starts are explicit."""
import hashlib
import json
import os
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .contracts import canonical_hash

API_ORIGIN = "https://api.apify.com"
ACTOR_ID = "f7ggUvGaOrrUuPkZQ"
TERMINAL = {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}
NONTERMINAL = {"READY", "RUNNING", "TIMING-OUT", "ABORTING"}
SAFE_HEADERS = {"content-type", "x-apify-pagination-offset", "x-apify-pagination-count", "x-apify-pagination-limit", "x-apify-pagination-total"}


class ExecutionGateError(RuntimeError):
    """A local safety gate prevented provider execution."""


class AdapterError(RuntimeError):
    def __init__(self, category, message, retry_after=None):
        self.category = category
        self.retry_after = retry_after
        super().__init__("{}: {}".format(category, message))


def _dt(value, field):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        raise ExecutionGateError("invalid_" + field)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ExecutionGateError("timezone_required_" + field)
    return result.astimezone(timezone.utc)


def _subtract_months(value, months):
    import calendar
    month = value.month - 1 - months
    year = value.year + month // 12
    month = month % 12 + 1
    return value.replace(year=year, month=month, day=min(value.day, calendar.monthrange(year, month)[1]))


def _money(value, field):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ExecutionGateError("invalid_" + field)
    if not amount.is_finite() or amount <= 0:
        raise ExecutionGateError("invalid_" + field)
    return amount


def _provider_id(value, field):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value):
        raise AdapterError("invalid_" + field, "provider returned an invalid identifier")
    return value


def _evidence(path, field):
    if not isinstance(path, str) or not path.strip() or not Path(path).is_file():
        raise ExecutionGateError("missing_" + field + "_evidence")


def build_request(config, *, query_id, results_wanted, charge_cap_usd, campaign_root, now=None):
    """Validate local gates and construct an exact sanitized request preview."""
    errors = []
    if not isinstance(config, dict) or config.get("schema_version") != "job-collection-v1":
        errors.append("unsupported_config_schema")
    if config.get("live_collection_enabled") is not True:
        errors.append("live_collection_disabled")
    queries = config.get("queries", [])
    query = next((row for row in queries if row.get("query_id") == query_id and row.get("status", "enabled") == "enabled"), None)
    if query is None:
        errors.append("unknown_or_disabled_query")
    try:
        start = _dt(config.get("window_start"), "window_start")
        end = _dt(config.get("window_end"), "window_end")
        if start >= end or start < _subtract_months(end, 12):
            errors.append("window_outside_supported_range")
    except ExecutionGateError as exc:
        errors.append(str(exc))
        start = end = None
    current = _dt(now or datetime.now(timezone.utc).isoformat(), "now")
    if end is not None and (end > current or (current - end).total_seconds() > 3600):
        errors.append("stale_window_end")
    if not isinstance(results_wanted, int) or isinstance(results_wanted, bool) or results_wanted < 1:
        errors.append("invalid_results_wanted")
    adapter = config.get("live_adapter") or {}
    core_ids = config.get("pilot_core_query_ids")
    optional_ids = config.get("pilot_optional_query_ids", [])
    query_rows = {row.get("query_id"): row for row in queries if isinstance(row, dict)}
    configured_ids = set(query_rows)
    valid_core_list = (isinstance(queries, list) and len(query_rows) == len(queries) and
                       isinstance(core_ids, list) and
                       all(isinstance(qid, str) for qid in core_ids) and
                       len(set(core_ids)) == len(core_ids) and set(core_ids) <= configured_ids)
    if not valid_core_list:
        errors.append("pilot_core_query_scope_invalid")
    elif len(core_ids) == 4:
        if optional_ids != []:
            errors.append("pilot_four_game_mode_has_no_optional_queries")
        core_rows = [query_rows[qid] for qid in core_ids]
        if any(row.get("family") != "Game Development" or row.get("status", "enabled") != "enabled"
               for row in core_rows):
            errors.append("pilot_four_core_queries_must_be_game_development_only")
    elif len(core_ids) == 6:
        if [query_rows[qid].get("family") for qid in core_ids[:5]] != [
                "Intelligent Systems", "Game Development", "Network Technology", "Web Development", "Shared/core"]:
            errors.append("pilot_core_queries_must_cover_four_tracks_and_shared_work")
        if any(query_rows[qid].get("status", "enabled") != "enabled" for qid in core_ids):
            errors.append("pilot_core_queries_must_be_enabled")
    else:
        errors.append("pilot_requires_six_core_or_four_game_queries")
    if (not isinstance(optional_ids, list) or len(optional_ids) > 2 or
            any(not isinstance(qid, str) for qid in optional_ids) or
            len(set(optional_ids)) != len(optional_ids) or not set(optional_ids) <= configured_ids or
            isinstance(core_ids, list) and bool(set(optional_ids) & set(core_ids))):
        errors.append("invalid_conditional_query_scope")
    elif any(query_rows[qid].get("status", "enabled") != "enabled" for qid in optional_ids):
        errors.append("conditional_queries_must_be_enabled")
    if query_id not in (core_ids or []) and query_id not in (optional_ids if isinstance(optional_ids, list) else []):
        errors.append("query_outside_pilot_scope")
    required = ("actor_id", "actor_name", "build_number", "build_id", "actor_contract_sha256", "actor_contract_verified_at",
                "actor_contract_evidence", "allowance_verified_at", "allowance_evidence", "verified_available_usd",
                "allowance_snapshot_basis", "allowance_reconciliation_evidence", "campaign_ceiling_usd", "baseline_spend_usd", "per_run_cap_usd",
                "source_access_basis", "authorized_collection_scope",
                "timeout_secs", "memory_mbytes", "max_results_per_run")
    errors.extend("missing_" + key for key in required if adapter.get(key) in (None, "", {}))
    for key in ("actor_contract_evidence", "allowance_evidence", "allowance_reconciliation_evidence"):
        if adapter.get(key):
            try:
                _evidence(adapter[key], key)
            except ExecutionGateError as exc:
                errors.append(str(exc))
    if adapter.get("actor_contract_evidence") and re.fullmatch(r"[0-9a-fA-F]{64}", str(adapter.get("actor_contract_sha256", ""))):
        try:
            actual_hash = hashlib.sha256(Path(adapter["actor_contract_evidence"]).read_bytes()).hexdigest()
            if actual_hash != str(adapter["actor_contract_sha256"]).lower(): errors.append("actor_contract_evidence_hash_mismatch")
        except OSError:
            errors.append("missing_actor_contract_evidence")
    if not isinstance(adapter.get("source_access_basis"), dict) or not adapter.get("source_access_basis", {}).get("basis") or not adapter.get("source_access_basis", {}).get("evidence"):
        errors.append("missing_source_access_basis")
    elif isinstance(adapter["source_access_basis"], dict):
        try: _evidence(adapter["source_access_basis"].get("evidence"), "source_access")
        except ExecutionGateError as exc: errors.append(str(exc))
    scope = adapter.get("authorized_collection_scope")
    if not isinstance(scope, dict) or not scope.get("reference") or not scope.get("evidence"):
        errors.append("missing_authorized_collection_scope")
    else:
        try: _evidence(scope.get("evidence"), "authorization")
        except ExecutionGateError as exc: errors.append(str(exc))
        if (scope.get("campaign_id") != config.get("campaign_id") or
                not isinstance(scope.get("query_ids"), list) or query_id not in scope.get("query_ids", [])):
            errors.append("authorization_scope_mismatch")
        try:
            if _dt(scope.get("window_start"), "authorized_window_start") != start or _dt(scope.get("window_end"), "authorized_window_end") != end:
                errors.append("authorization_window_mismatch")
            if Decimal(str(scope.get("max_charge_usd"))) < Decimal(str(charge_cap_usd)):
                errors.append("authorization_charge_limit_exceeded")
        except (ExecutionGateError, InvalidOperation, TypeError, ValueError):
            errors.append("invalid_authorized_collection_scope")
    try:
        contract_hash = str(adapter.get("actor_contract_sha256", ""))
        if not re.fullmatch(r"[0-9a-fA-F]{64}", contract_hash): errors.append("invalid_actor_contract_hash")
        contract_time = _dt(adapter.get("actor_contract_verified_at"), "contract_timestamp")
        allowance_time = _dt(adapter.get("allowance_verified_at"), "allowance_timestamp")
        if (current - allowance_time).total_seconds() > 24 * 3600 or allowance_time > current:
            errors.append("stale_allowance_evidence")
        if (current - contract_time).total_seconds() > 30 * 86400 or contract_time > current:
            errors.append("stale_contract_evidence")
        verified = _money(adapter.get("verified_available_usd"), "verified_available_usd")
        ceiling = _money(adapter.get("campaign_ceiling_usd"), "campaign_ceiling_usd")
        per_run_ceiling = _money(adapter.get("per_run_cap_usd"), "per_run_cap_usd")
        baseline = Decimal(str(adapter.get("baseline_spend_usd")))
        cap = _money(charge_cap_usd, "charge_cap_usd")
        if not baseline.is_finite() or baseline < 0: errors.append("invalid_baseline_spend_usd")
        if ceiling > min(Decimal("0.30"), verified): errors.append("campaign_ceiling_exceeds_pilot_limit")
        if per_run_ceiling > Decimal("0.05"): errors.append("configured_per_run_cap_exceeds_pilot_limit")
        if cap > per_run_ceiling: errors.append("charge_cap_exceeds_configured_per_run_cap")
        if cap > ceiling - baseline: errors.append("charge_cap_exceeds_remaining_campaign_funds")
    except (ExecutionGateError, InvalidOperation, TypeError, ValueError) as exc:
        errors.append(str(exc) or "invalid_budget")
        cap = Decimal("0")
    if adapter.get("actor_id") != ACTOR_ID:
        errors.append("unexpected_actor_id")
    if adapter.get("actor_name") != "shahidirfan/jobstreet-scraper": errors.append("unexpected_actor_name")
    if adapter.get("build_number") != "0.0.36" or adapter.get("build_id") != "wcMB0BeF4w9asSke8": errors.append("unexpected_pinned_build")
    if not isinstance(adapter.get("timeout_secs"), int) or isinstance(adapter.get("timeout_secs"), bool) or not 1 <= adapter.get("timeout_secs", 0) <= 300: errors.append("invalid_timeout_secs")
    if not isinstance(adapter.get("memory_mbytes"), int) or isinstance(adapter.get("memory_mbytes"), bool) or not 1 <= adapter.get("memory_mbytes", 0) <= 1024: errors.append("invalid_memory_mbytes")
    if (not isinstance(adapter.get("max_results_per_run"), int) or isinstance(adapter.get("max_results_per_run"), bool) or
            not 1 <= adapter.get("max_results_per_run", 0) <= 25 or
            isinstance(results_wanted, int) and results_wanted > adapter.get("max_results_per_run", 0)):
        errors.append("results_limit_exceeded")
    if adapter.get("timeout_secs") != 300:
        errors.append("pilot_timeout_must_be_300_seconds")
    if cap > Decimal("0.05"):
        errors.append("pilot_per_run_cap_exceeds_0.05_usd")
    if errors:
        raise ExecutionGateError("Live collection blocked: " + ", ".join(dict.fromkeys(errors)))
    # ponytail: actor date filters are relative; reject stale frozen windows instead of silently widening them.
    span = (end - start).total_seconds()
    posted = "24h" if span <= 86400 else "7d" if span <= 7 * 86400 else "30d" if span <= 30 * 86400 else "anytime"
    payload = {"keyword": query["keyword"], "location": "", "country": "ph", "posted_date": posted,
               "results_wanted": results_wanted, "proxyConfiguration": {"useApifyProxy": False}}
    return {"request_id": str(uuid.uuid4()), "campaign_id": config.get("campaign_id"), "query_id": query_id,
            "input": payload, "run_options": {"build": adapter["build_number"], "timeout": adapter["timeout_secs"],
            "memory": adapter["memory_mbytes"], "maxTotalChargeUsd": float(cap), "restartOnError": False},
            "reserved_usd": str(cap), "window_start": config["window_start"], "window_end": config["window_end"],
            "pilot_stage": "core" if query_id in core_ids else "conditional",
            "query_registry_sha256": canonical_hash(queries), "config_sha256": canonical_hash(config),
            "actor_id": adapter["actor_id"], "actor_name": adapter["actor_name"],
            "expected_build_id": adapter["build_id"], "expected_build_number": adapter["build_number"],
            "contract_sha256": adapter["actor_contract_sha256"], "actor_contract_evidence": adapter["actor_contract_evidence"],
            "gate_evidence": {"actor_contract_verified_at": adapter["actor_contract_verified_at"],
                "allowance_verified_at": adapter["allowance_verified_at"], "allowance_evidence": adapter["allowance_evidence"],
                "verified_available_usd": str(verified), "campaign_ceiling_usd": str(ceiling),
                "baseline_spend_usd": str(baseline), "allowance_snapshot_basis": adapter["allowance_snapshot_basis"],
                "allowance_reconciliation_evidence": adapter["allowance_reconciliation_evidence"],
                "source_access_basis": adapter["source_access_basis"], "authorized_collection_scope": adapter["authorized_collection_scope"]},
            "campaign_root": str(Path(campaign_root).resolve()),
            "coverage_warning": "anytime_filter_cannot_guarantee_historical_supply" if posted == "anytime" else None}


def verify_execution_gate(config=None, **kwargs):
    if config is None:
        raise ExecutionGateError("Live collection blocked: campaign_config_required")
    return build_request(config, **kwargs)


def load_token(repository_root):
    token = os.environ.get("APIFY_API_TOKEN")
    if token is None:
        try:
            from dotenv import load_dotenv
        except ImportError as exc:
            raise ExecutionGateError("python-dotenv is required to load repository .env") from exc
        load_dotenv(dotenv_path=Path(repository_root) / ".env", override=False)
        token = os.environ.get("APIFY_API_TOKEN")
    if not token or not token.strip():
        raise ExecutionGateError("APIFY_API_TOKEN is missing or blank")
    return token.strip()


def sanitize(value, token=None):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            if str(key).lower() in {"token", "authorization", "cookie", "password", "secret", "api_token"}:
                continue
            result[key] = sanitize(child, token)
        return result
    if isinstance(value, list): return [sanitize(child, token) for child in value]
    if isinstance(value, str):
        text = value.replace(token, "[REDACTED]") if token else value
        return re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1[REDACTED]", text)
    return value


class ApifyTransport:
    def __init__(self, token, request_fn=None):
        self.token = token
        self.request_fn = request_fn or self._request

    @staticmethod
    def _request(method, path, query, body, timeout, headers):
        from urllib.parse import urlencode
        encoded_query = {key: str(value).lower() if isinstance(value, bool) else value
                         for key, value in query.items()}
        url = API_ORIGIN + path + (("?" + urlencode(encoded_query)) if query else "")
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(url, data=data, method=method, headers=headers)
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl): return None
        opener = build_opener(NoRedirect())
        try:
            with opener.open(req, timeout=timeout) as response:
                payload = response.read()
                decoded = json.loads(payload.decode("utf-8")) if payload else None
                return decoded, {k.lower(): v for k, v in response.headers.items() if k.lower() in SAFE_HEADERS}
        except HTTPError as exc:
            message = sanitize(exc.read().decode("utf-8", "replace"), headers.get("Authorization", "").replace("Bearer ", ""))
            raise AdapterError("http_{}".format(exc.code), str(message), retry_after=exc.headers.get("Retry-After"))
        except (URLError, TimeoutError, OSError) as exc:
            raise AdapterError("network_error", str(sanitize(str(exc), headers.get("Authorization", "").replace("Bearer ", ""))))

    def request(self, method, path, query=None, body=None, timeout=30):
        headers = {"Authorization": "Bearer " + self.token, "Accept": "application/json"}
        if body is not None: headers["Content-Type"] = "application/json"
        return self.request_fn(method, path, query or {}, body, timeout, headers)


def preflight(config, request, transport):
    actor_id = request["actor_id"]
    actor, _ = transport.request("GET", "/v2/acts/" + actor_id, timeout=30)
    build_path = "/v2/actors/{}/builds/{}".format(actor_id, request["expected_build_id"])
    build, _ = transport.request("GET", build_path, timeout=30)
    actor = actor.get("data", actor) if isinstance(actor, dict) else actor
    build = build.get("data", build) if isinstance(build, dict) else build
    if not actor or actor.get("id") != actor_id or not build or build.get("buildNumber") != request["expected_build_number"] or build.get("id") != request["expected_build_id"]:
        raise AdapterError("contract_changed", "actor or pinned build identity does not match local evidence")
    snapshot_path = Path(request["actor_contract_evidence"])
    if hashlib.sha256(snapshot_path.read_bytes()).hexdigest() != request["contract_sha256"].lower():
        raise AdapterError("contract_changed", "saved actor contract hash does not match its evidence file")
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    live_input = (build.get("actorDefinition") or {}).get("input")
    expected_input = snapshot.get("input_schema")
    def contract_shape(schema):
        if isinstance(schema, dict):
            return {key: contract_shape(value) for key, value in schema.items()
                    if key not in {"editor", "enumTitles"}}
        if isinstance(schema, list):
            return [contract_shape(value) for value in schema]
        return schema
    compatible_input = isinstance(live_input, dict) and isinstance(expected_input, dict)
    if compatible_input:
        # This is a behavioral constraint already enforced by build_request.
        live_shape = contract_shape(live_input)
        if (isinstance(live_shape.get("properties"), dict) and
                live_shape["properties"].get("results_wanted", {}).get("minimum") == 1 and
                "minimum" not in expected_input.get("properties", {}).get("results_wanted", {})):
            live_shape["properties"]["results_wanted"].pop("minimum")
        compatible_input = canonical_hash(live_shape) == canonical_hash(contract_shape(expected_input))
    if not compatible_input:
        raise AdapterError("contract_changed", "pinned build input schema differs from the saved actor contract")
    pricing_rows = actor.get("pricingInfos") or []
    now = datetime.now(timezone.utc)
    active = []
    for row in pricing_rows:
        try:
            if _dt(row.get("startedAt"), "pricing_started_at") <= now: active.append(row)
        except ExecutionGateError: pass
    if not active:
        raise AdapterError("pricing_unavailable", "Apify did not return an active pricing record")
    pricing = max(active, key=lambda row: row.get("startedAt", ""))
    minimum_cap = pricing.get("minimalMaxTotalChargeUsd")
    if minimum_cap is not None and Decimal(request["reserved_usd"]) < Decimal(str(minimum_cap)):
        raise AdapterError("charge_cap_below_provider_minimum", "reserved cap is below the current actor's minimum")
    baseline_events = snapshot.get("pricing", {}).get("events", [])
    live_events = (pricing.get("pricingPerEvent") or {}).get("actorChargeEvents") or {}
    normalized_live = {str(value.get("eventTitle", "")).strip().lower(): value for value in live_events.values()}
    if pricing.get("pricingModel") != snapshot.get("pricing", {}).get("model") or not baseline_events:
        raise AdapterError("contract_changed", "live actor pricing model differs from the saved contract")
    for expected in baseline_events:
        actual = normalized_live.get(str(expected.get("title", "")).strip().lower())
        if not actual:
            raise AdapterError("contract_changed", "a saved billable event is missing from current pricing")
        if "tieredPricing" in expected:
            actual_tiers = actual.get("eventTieredPricingUsd") or {}
            for tier in expected["tieredPricing"]:
                current_price = actual_tiers.get(tier["tier"])
                if isinstance(current_price, dict): current_price = current_price.get("tieredEventPriceUsd")
                if current_price is None or Decimal(str(current_price)) != Decimal(str(tier["priceUsd"])):
                    raise AdapterError("contract_changed", "tiered event pricing differs from the saved contract")
        elif Decimal(str(actual.get("eventPriceUsd", "NaN"))) != Decimal(str(expected.get("priceUsd", "NaN"))):
            raise AdapterError("contract_changed", "flat event pricing differs from the saved contract")
    # Apify's generic account identity endpoint is intentionally not treated as allowance evidence.
    return sanitize({"actor_id": actor_id, "build_id": build.get("id"), "build_number": build.get("buildNumber"),
                     "pricing_info": pricing, "preflighted_at": datetime.now(timezone.utc).isoformat()}, transport.token)


def _atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    tmp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(path))


def start_run(request, transport, state):
    state.reserve(request)
    try:
        response, _ = transport.request("POST", "/v2/actors/{}/runs".format(request["actor_id"]),
                                        query=request["run_options"], body=request["input"], timeout=30)
    except Exception as exc:
        category = exc.category if isinstance(exc, AdapterError) else "unexpected_transport_error"
        detail = str(exc) if isinstance(exc, AdapterError) else type(exc).__name__
        message = sanitize(detail, transport.token)[:2000]
        state.update(request["request_id"], "start_outcome_unknown", last_error_category=category,
                     last_error_message=message, start_error_category=category, start_error_message=message)
        raise AdapterError("start_outcome_unknown", "start outcome is unknown; reconcile in Apify Console before resuming") from exc
    run = response.get("data") if isinstance(response, dict) and isinstance(response.get("data"), dict) else response
    if not isinstance(run, dict) or not run.get("id"):
        state.update(request["request_id"], "start_outcome_unknown", last_error_category="malformed_start_response")
        raise AdapterError("start_outcome_unknown", "response has no run ID; reconcile before another start")
    _provider_id(run["id"], "run_id")
    options = run.get("options") or {}
    try:
        expected_cap = Decimal(str(options.get("maxTotalChargeUsd"))) == Decimal(request["reserved_usd"])
    except InvalidOperation:
        expected_cap = False
    expected = (run.get("actId") == request["actor_id"] and run.get("buildId") == request["expected_build_id"] and
                options.get("build") == request["expected_build_number"] and
                options.get("timeoutSecs") == request["run_options"]["timeout"] and
                options.get("memoryMbytes") == request["run_options"]["memory"] and
                options.get("restartOnError") is False and expected_cap)
    if not expected:
        state.update(request["request_id"], "contract_mismatch", run_id=run["id"], default_dataset_id=run.get("defaultDatasetId"),
                     billing_status="unknown", provider_run=sanitize(run, transport.token),
                     last_error_category="effective_build_mismatch")
        _atomic_json(Path(request["campaign_root"]) / "raw" / run["id"] / "run.json",
                     {"request_id": request["request_id"], "run": sanitize(run, transport.token),
                      "request": {k: v for k, v in request.items() if k != "campaign_root"}})
        raise AdapterError("effective_build_mismatch", "run saved; effective actor/build differs from request")
    state.update(request["request_id"], "running", run_id=run["id"], dataset_id=run.get("defaultDatasetId"),
                 provider_status=run.get("status"), provider_run=sanitize(run, transport.token))
    return run


def _get_retry(transport, path, query=None, timeout=30, sleep=time.sleep):
    for attempt, delay in enumerate((1, 2, 4), 1):
        try:
            return transport.request("GET", path, query=query, timeout=timeout)
        except AdapterError as exc:
            if attempt == 3 or not (exc.category.startswith("http_429") or exc.category.startswith("http_5") or exc.category == "network_error"):
                raise
            try:
                wait = min(30.0, max(0.0, float(exc.retry_after))) if exc.retry_after is not None else delay
            except (TypeError, ValueError):
                wait = delay
            sleep(wait)


def poll_run(run_id, transport, state, request_id, *, timeout_secs, clock=time.monotonic, sleep=time.sleep):
    _provider_id(run_id, "run_id")
    deadline = clock() + timeout_secs + 120
    while clock() < deadline:
        response, _ = _get_retry(transport, "/v2/actor-runs/" + run_id, timeout=30, sleep=sleep)
        run = response.get("data", response) if isinstance(response, dict) else response
        status = run.get("status") if isinstance(run, dict) else None
        state.update(request_id, "running", provider_status=status, provider_run=sanitize(run, transport.token))
        if status in TERMINAL:
            return run
        if status not in NONTERMINAL:
            raise AdapterError("unexpected_run_status", "run status was not recognized; checkpoint retained")
        sleep(5)
    raise AdapterError("poll_deadline", "remote run remains active; resume the same request")


def download_dataset(run, transport, state, request_id, *, page_size=1000, clock=time.time, sleep=time.sleep):
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        raise AdapterError("missing_dataset_id", "run has no default dataset ID")
    _provider_id(dataset_id, "dataset_id")
    if run.get("id"): _provider_id(run["id"], "run_id")
    request = state.get(request_id)
    campaign = Path(request["campaign_root"])
    folder = campaign / "raw" / run.get("id", request.get("run_id", "unknown"))
    pages = folder / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    metadata, _ = _get_retry(transport, "/v2/datasets/" + dataset_id, query={"limit": 0}, sleep=sleep)
    dataset = metadata.get("data", metadata) if isinstance(metadata, dict) else {}
    expected_total = dataset.get("itemCount")
    if not isinstance(expected_total, int) or expected_total < 0:
        raise AdapterError("invalid_dataset_metadata", "dataset item count is unavailable")
    # A successful run can become visible before its default dataset is populated.
    # Require three matching metadata reads before accepting an empty dataset.
    if expected_total == 0:
        stable_reads = 1
        for _ in range(5):
            if stable_reads >= 3:
                break
            sleep(2)
            refreshed, _ = _get_retry(transport, "/v2/datasets/" + dataset_id, query={"limit": 0}, sleep=sleep)
            refreshed_data = refreshed.get("data", refreshed) if isinstance(refreshed, dict) else {}
            refreshed_total = refreshed_data.get("itemCount")
            if not isinstance(refreshed_total, int) or refreshed_total < 0:
                raise AdapterError("invalid_dataset_metadata", "dataset item count is unavailable")
            if refreshed_total != expected_total:
                expected_total = refreshed_total
                stable_reads = 1
            else:
                stable_reads += 1
            dataset = refreshed_data
    state.update(request_id, "downloading", dataset_id=dataset_id, expected_total=expected_total)
    offset = 0
    combined = []
    while offset < expected_total:
        page_path = pages / (str(offset) + ".json")
        meta_path = pages / (str(offset) + ".metadata.json")
        if page_path.exists() and meta_path.exists():
            saved = json.loads(page_path.read_text(encoding="utf-8"))
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if (meta.get("sha256") == hashlib.sha256(page_path.read_bytes()).hexdigest() and
                    meta.get("offset") == offset and meta.get("count") == len(saved) and meta.get("total") == expected_total):
                page = saved
            else:
                raise AdapterError("saved_page_integrity_error", "saved dataset page failed its checkpoint hash/count/total")
        elif page_path.exists():
            # A crash may occur after the source page is atomically saved and before metadata.
            # Rebuild only the missing checkpoint; never replace an already saved page.
            try: page = json.loads(page_path.read_text(encoding="utf-8"))
            except (ValueError, OSError) as exc: raise AdapterError("saved_page_integrity_error", "orphaned page is not valid JSON") from exc
            if not isinstance(page, list) or not page or len(page) > page_size:
                raise AdapterError("saved_page_integrity_error", "orphaned page body is invalid")
            raw = page_path.read_bytes()
            _atomic_json(meta_path, {"offset": offset, "count": len(page), "total": expected_total,
                "retrieved_at": datetime.now(timezone.utc).isoformat(), "sha256": hashlib.sha256(raw).hexdigest(),
                "recovered_checkpoint": True, "headers": {}})
        else: page = None
        headers = {}
        if page is None:
            page, headers = _get_retry(transport, "/v2/datasets/{}/items".format(dataset_id),
                query={"offset": offset, "limit": page_size, "desc": False, "clean": False,
                       "skipHidden": False, "skipEmpty": False}, sleep=sleep)
            if not isinstance(page, list) or not page or len(page) > page_size:
                raise AdapterError("invalid_dataset_page", "unexpected page body or empty page before advertised total")
            page_offset = headers.get("x-apify-pagination-offset")
            page_count = headers.get("x-apify-pagination-count")
            if page_offset is not None and int(page_offset) != offset:
                raise AdapterError("invalid_dataset_page", "pagination offset differs from requested offset")
            if page_count is not None and int(page_count) != len(page):
                raise AdapterError("invalid_dataset_page", "pagination count differs from page body")
            page_total = headers.get("x-apify-pagination-total")
            if page_total is not None and int(page_total) != expected_total:
                raise AdapterError("dataset_total_changed", "pagination total differs from dataset metadata")
            raw = json.dumps(page, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            tmp = page_path.with_suffix(".json.tmp")
            tmp.write_bytes(raw); os.replace(str(tmp), str(page_path))
            _atomic_json(meta_path, {"offset": offset, "count": len(page), "total": expected_total,
                                     "retrieved_at": datetime.now(timezone.utc).isoformat(), "sha256": hashlib.sha256(raw).hexdigest(),
                                     "headers": {k: v for k, v in headers.items() if k in SAFE_HEADERS}})
        combined.extend(page)
        offset += len(page)
        state.update(request_id, "downloading", next_dataset_offset=offset)
    final_metadata, _ = _get_retry(transport, "/v2/datasets/" + dataset_id, query={"limit": 0}, sleep=sleep)
    final_data = final_metadata.get("data", final_metadata) if isinstance(final_metadata, dict) else {}
    if final_data.get("itemCount") != expected_total:
        raise AdapterError("dataset_total_changed", "dataset total changed while downloading")
    if len(combined) != expected_total:
        raise AdapterError("dataset_count_mismatch", "retrieved count differs from dataset metadata")
    _atomic_json(folder / "dataset.json", combined)
    digest = hashlib.sha256((folder / "dataset.json").read_bytes()).hexdigest()
    state.update(request_id, "downloaded", dataset_id=dataset_id, returned_count=len(combined), dataset_sha256=digest)
    return folder / "dataset.json"


def run_metadata(run, request, dataset_id, imported_status="downloaded"):
    return {"run_id": run.get("id"), "query_id": request["query_id"], "dataset_id": dataset_id,
            "actor_id": run.get("actId", request["actor_id"]), "actor": request.get("actor_name"),
            "build_id": run.get("buildId", request["expected_build_id"]), "build": request.get("expected_build_number"),
            "started_at": run.get("startedAt"), "finished_at": run.get("finishedAt"), "status": run.get("status"),
            "provider_status": run.get("status"), "import_status": imported_status,
            "actual_run_options": sanitize(run.get("options", {})),
            "requested_run_options": request.get("run_options"),
            "provider_charge_usd": (run.get("usageTotalUsd") if run.get("usageTotalUsd") is not None
                                     else run.get("chargedUsd")),
            "charged_event_counts": run.get("chargedEventCounts"), "pricing_info": sanitize(run.get("pricingInfo", {}))}
