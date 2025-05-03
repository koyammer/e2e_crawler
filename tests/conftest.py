
import pytest

@pytest.fixture(autouse=True)
def _capture_console_errors(page):
    errors=[]
    page.on("pageerror", lambda e: errors.append(e.message))
    page.on("console", lambda msg: errors.append(msg.text) if msg.type=="error" else None)
    yield
    assert not errors, f"JavaScript errors: {errors}"
