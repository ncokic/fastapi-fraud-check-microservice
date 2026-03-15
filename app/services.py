import joblib
import numpy as np
from app.schemas import FraudAnalysisRequest


class FraudChecker:
    def __init__(self, model_path: str, scaler_path: str):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def predict(self, payload: FraudAnalysisRequest):
        features = np.array([[
            payload.order_amount,
            payload.orders_last_24h,
            payload.is_address_mismatch,
            payload.is_country_mismatch,
            payload.account_age_min
        ]])
        scaled_features = self.scaler.transform(features)
        probability = self.model.predict_proba(scaled_features)[0][1]

        return {
            "order_id": payload.order_id,
            "is_flagged": probability > 0.7,
            "risk_score": round(probability * 100)
        }