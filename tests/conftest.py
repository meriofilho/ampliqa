"""Os dados reais do laboratório (tests/data, example-data) não vão para o repositório público.
Quando um teste precisa deles e eles não existem, o teste é pulado em vez de falhar."""
from pathlib import Path

import pytest

PRIVATE = [Path(__file__).parent / "data", Path(__file__).parent.parent / "example-data"]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if call.excinfo is not None and call.excinfo.errisinstance(FileNotFoundError):
        missing = Path(str(getattr(call.excinfo.value, "filename", "") or ""))
        if any(p in missing.parents for p in PRIVATE):
            rep.outcome = "skipped"
            rep.longrepr = (str(item.path), item.location[1] or 0, f"dados privados ausentes: {missing.name}")
