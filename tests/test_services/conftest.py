from unittest.mock import MagicMock

import pytest

from app.schemas import FraudAnalysisRequest
from app.services import FraudCheckerService


@pytest.fixture
def mock_fraud_service():
    mocks = {
        "model": MagicMock(),
        "scaler": MagicMock()
    }
    service = FraudCheckerService(**mocks)
    return service, mocks


@pytest.fixture
def base_payload():
    return FraudAnalysisRequest(
        order_id=1,
        user_id=1,
        order_amount=49.99,
        orders_last_24h=1,
        is_shipping_billing_mismatch=False,
        shipping_country="US",
        ip_country="US",
        account_age_min=5000
    )