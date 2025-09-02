from src.services.costs.in_memory import InMemoryCostLedger


def test_in_memory_cost_ledger_basic_flow():
    ledger = InMemoryCostLedger(monthly_cap_usd=10.0)
    # Ensure clean slate for the current month (class-level shared state)
    ledger.reset_month()

    # Initially zero
    status = ledger.status()
    assert status.used_usd == 0.0
    assert status.cap_usd == 10.0

    # Can spend under cap
    assert ledger.can_spend(3.0)

    # Commit cost and verify
    ledger.commit(3.0)
    status = ledger.status()
    assert abs(status.used_usd - 3.0) < 1e-9

    # Precheck should pass for small add
    ledger.precheck(2.0)

    # Precheck should fail if exceeding cap
    try:
        ledger.precheck(8.0)
        assert False, "Expected Exception for exceeding monthly cap"
    except Exception as e:
        assert "cap" in str(e).lower()

    # Reset current month and verify
    ledger.reset_month()
    assert ledger.status().used_usd == 0.0
