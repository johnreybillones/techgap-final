"""Apify boundary. This module deliberately provides no live execution path yet."""


class ExecutionGateError(RuntimeError):
    pass


def verify_execution_gate(*, allowance_verified_at=None, source_access_basis=None,
                          charge_cap_usd=None, actor_contract_verified=False):
    missing = []
    if not allowance_verified_at: missing.append("verified_account_allowance")
    if not source_access_basis: missing.append("source_access_basis")
    if charge_cap_usd is None or charge_cap_usd <= 0: missing.append("positive_run_charge_cap")
    if not actor_contract_verified: missing.append("verified_actor_contract")
    if missing:
        raise ExecutionGateError("Live collection blocked: " + ", ".join(missing))
    raise ExecutionGateError("Live collection is not implemented; import saved run evidence instead")
