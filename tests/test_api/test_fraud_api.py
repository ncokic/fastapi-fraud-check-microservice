import pytest

from scripts.generate_hmac_signature import generate_hmac_signature


ECOMMERCE_PAYLOAD = {
    "order_id": 100,
    "user_id": 75,
    "order_amount": 129.99,
    "orders_last_24h": 1,
    "is_shipping_billing_mismatch": False,
    "shipping_country": "US",
    "ip_country": "US",
    "account_age_min": 10000
}


def test_check_fraud_happy_path(client):
    headers = {"X-Signature": generate_hmac_signature(ECOMMERCE_PAYLOAD)}
    response = client.post("/check_fraud", json=ECOMMERCE_PAYLOAD, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_assessment"] in ["low", "medium", "high"]
    assert isinstance(data["risk_score"], float)

@pytest.mark.parametrize("key, value, expected_status", [
    pytest.param("orders_last_24h", 1, 200, id="valid_signature"),
    pytest.param("orders_last_24h", "one", 422, id="invalid_field_type"),
    pytest.param("shipping_country", "United States", 422, id="wrong_country_format")
])
def test_fraud_check_payload_validation(client, override_signature, key, value, expected_status):
    payload = ECOMMERCE_PAYLOAD | {key: value}
    response = client.post("/check_fraud", json=payload)
    assert response.status_code == expected_status

def test_fraud_check_missing_field(client, override_signature):
    payload = ECOMMERCE_PAYLOAD.copy()
    payload.pop("orders_last_24h")
    response = client.post("/check_fraud", json=payload)
    assert response.status_code == 422

@pytest.mark.parametrize("signature, expected_status", [
    pytest.param(generate_hmac_signature(ECOMMERCE_PAYLOAD), 200, id="valid_signature"),
    pytest.param(generate_hmac_signature(ECOMMERCE_PAYLOAD) + "a", 401, id="invalid_signature"),
    pytest.param("", 401, id="missing_signature")
])
def test_fraud_check_signature_validation(client, signature, expected_status):
    headers = {"X-Signature": signature}
    print(ECOMMERCE_PAYLOAD)
    response = client.post("/check_fraud", json=ECOMMERCE_PAYLOAD, headers=headers)
    assert response.status_code == expected_status
    if response.status_code == 401:
        assert "invalid" in response.json()["detail"].lower()

def test_high_risk_guardrail_applied(client, override_signature):
    payload = {
        **ECOMMERCE_PAYLOAD,
        "orders_last_24h": 5,
        "is_shipping_billing_mismatch": True,
        "ip_country": "GB",
        "account_age_min": 10
    }
    response = client.post("/check_fraud", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_assessment"] == "high"