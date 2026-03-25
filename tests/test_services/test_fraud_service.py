import pytest


def setup_low_risk_model(mocks):
    mocks["scaler"].transform.return_value = [[1, 2, 3]]
    mocks["model"].predict_proba.return_value = [[0.9, 0.1]]

def setup_medium_risk_model(mocks):
    mocks["scaler"].transform.return_value = [[1, 2, 3]]
    mocks["model"].predict_proba.return_value = [[0.4, 0.6]]

def setup_high_risk_model(mocks):
    mocks["scaler"].transform.return_value = [[1, 2, 3]]
    mocks["model"].predict_proba.return_value = [[0.1, 0.9]]

class TestFraudCheckerService:
    @pytest.mark.parametrize("setup_model, expected_risk", [
        pytest.param(setup_low_risk_model, "low", id="low_risk_response"),
        pytest.param(setup_medium_risk_model, "medium", id="medium_risk_response"),
        pytest.param(setup_high_risk_model, "high", id="high_risk_response")
    ])
    def test_model_risk_calculation_no_guardrails(
            self, mock_fraud_service, base_payload, setup_model, expected_risk
    ):
        service, mocks = mock_fraud_service
        setup_model(mocks)
        payload = base_payload.model_copy()
        result = service.predict(payload)
        assert result["risk_assessment"] == expected_risk
        assert result["reasons"] == "base_model_calculation"

    def test_guardrail_new_account_country_mismatch_medium_risk(self, mock_fraud_service, base_payload):
        service, mocks = mock_fraud_service
        setup_low_risk_model(mocks)

        payload = base_payload.model_copy()
        payload.account_age_min = 10
        payload.ip_country = "GB"
        payload.shipping_country = "US"

        result = service.predict(payload)
        assert result["risk_assessment"] == "medium"
        reasons = " ".join(result["reasons"]).lower()
        assert "new_account" in reasons
        assert "country_mismatch" in reasons

    def test_guardrail_country_mismatch_high_velocity_high_risk(self, mock_fraud_service, base_payload):
        service, mocks = mock_fraud_service
        setup_low_risk_model(mocks)

        payload = base_payload.model_copy()
        payload.ip_country = "GB"
        payload.shipping_country = "US"
        payload.orders_last_24h = 5

        result = service.predict(payload)
        assert result["risk_assessment"] == "high"
        reasons = " ".join(result["reasons"]).lower()
        assert "country_mismatch" in reasons
        assert "high_velocity" in reasons

    def test_high_amount_guardrail(self, mock_fraud_service, base_payload):
        service, mocks = mock_fraud_service
        setup_low_risk_model(mocks)

        payload = base_payload.model_copy()
        payload.order_amount = 1500

        result = service.predict(payload)
        assert result["risk_assessment"] == "medium"
        reasons = " ".join(result["reasons"]).lower()
        assert "high_order_amount" in reasons

    def test_guardrail_does_not_downgrade_risk(self, mock_fraud_service, base_payload):
        service, mocks = mock_fraud_service
        setup_high_risk_model(mocks)

        payload = base_payload.model_copy()
        payload.order_amount = 1500

        result = service.predict(payload)
        assert result["risk_assessment"] == "high"

    def test_group_features_structure(self, mock_fraud_service, base_payload):
        service = mock_fraud_service[0]
        payload_df = service._group_features(base_payload)
        assert list(payload_df.columns) == [
            "order_amount",
            "orders_last_24h",
            "address_mismatch",
            "country_mismatch",
            "account_age_min",
            "new_account",
            "high_velocity",
            "diff_country_new_acc",
            "diff_country_high_vel"
        ]