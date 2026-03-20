import joblib
import pandas as pd

from app.config import settings
from app.schemas import FraudAnalysisRequest


class FraudCheckerService:
    def __init__(self, model_path: str, scaler_path: str):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def predict(self, payload: FraudAnalysisRequest):
        features_df = self._group_features(payload)
        score = self._calculate_risk_score(features_df)
        base_risk = self._score_to_risk(score)
        final_risk, reasons = self._apply_guardrails(payload, base_risk)
        return {
            "order_id": payload.order_id,
            "risk_assessment": final_risk,
            "risk_score": round(score * 100),
            "reasons": reasons or "base_model_calculation"
        }

    @staticmethod
    def _group_features(payload: FraudAnalysisRequest) -> pd.DataFrame:
        features = {
            "order_amount": payload.order_amount,
            "orders_last_24h": payload.orders_last_24h,
            "address_mismatch": payload.is_address_mismatch,
            "country_mismatch": payload.is_country_mismatch,
            "account_age_min": payload.account_age_min,
            "new_account": payload.is_new_account,
            "high_velocity": payload.has_high_velocity,
            "diff_country_new_acc": payload.diff_country_new_acc,
            "diff_country_high_vel": payload.diff_country_high_vel
        }
        return pd.DataFrame([features])

    def _calculate_risk_score(self, features: pd.DataFrame) -> float:
        scaled_features = self.scaler.transform(features)
        return self.model.predict_proba(scaled_features)[0][1]

    @staticmethod
    def _score_to_risk(score: float) -> str:
        if score >= settings.HIGH_RISK_THRESHOLD:
            return "high"
        elif score >= settings.MEDIUM_RISK_THRESHOLD:
            return "medium"
        else:
            return "low"

    @staticmethod
    def _apply_guardrails(payload: FraudAnalysisRequest, base_risk: str) -> tuple[str, list[str] | None]:
        risk = base_risk
        reasons = []

        if payload.is_new_account and payload.is_country_mismatch and payload.order_amount > 500:
            if risk != "high":
                risk = "high"
                reasons.append("new_account + country_mismatch + high_order_amount")
            return risk, reasons

        if payload.is_country_mismatch and payload.has_high_velocity:
            if risk != "high":
                risk = "high"
                reasons.append("country_mismatch + high_velocity")
            return risk, reasons

        if payload.is_new_account and payload.is_country_mismatch:
            if risk == "low":
                risk = "medium"
                reasons.append("new_account + country_mismatch")

        if payload.orders_last_24h >= 2 and payload.is_new_account and payload.is_address_mismatch:
            if risk == "low":
                risk = "medium"
                reasons.append("multiple_orders + new_account + address_mismatch")

        if payload.order_amount >= 1000:
            if risk == "low":
                risk = "medium"
                reasons.append("high_order_amount")

        return risk, reasons
