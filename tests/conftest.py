import pytest

from app.main import app
from app.utils.security import verify_hmac_signature


@pytest.fixture
def override_signature():
    app.dependency_overrides[verify_hmac_signature] = lambda: True
    yield
    app.dependency_overrides.pop(verify_hmac_signature, None)