import joblib
import pandas as pd

from app.config import settings
from app.schemas import FraudAnalysisRequest


class FraudCheckerService:
    def __init__(self, model_path: str, scaler_path: str):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def predict(self, payload: FraudAnalysisRequest):
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
        features_df = pd.DataFrame([features])
        scaled_features = self.scaler.transform(features_df)
        probability = self.model.predict_proba(scaled_features)[0][1]
        if probability >= settings.HIGH_RISK_THRESHOLD:
            risk_assessment = "high"
        elif probability >= settings.MEDIUM_RISK_THRESHOLD:
            risk_assessment = "medium"
        else:
            risk_assessment = "low"

        return {
            "order_id": payload.order_id,
            "risk_assessment": risk_assessment,
            "risk_score": round(probability * 100)
        }
