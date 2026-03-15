from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FraudAnalysisRequest(BaseModel):
    order_id: int
    user_id: int

    order_amount: Decimal = Field(gt=0)
    orders_last_24h: int = Field(gt=0)
    is_shipping_billing_mismatch: bool
    shipping_country: str = Field(min_length=2, max_length=2)
    ip_country: str = Field(min_length=2, max_length=2)

    account_created_at: datetime
    order_created_at: datetime

    @property
    def account_age_min(self) -> int:
        result = self.order_created_at - self.account_created_at
        return int(result.total_seconds() / 60)

    @property
    def is_country_mismatch(self) -> int:
        return 1 if self.shipping_country != self.ip_country else 0

    @property
    def is_address_mismatch(self) -> int:
        return 1 if self.is_shipping_billing_mismatch else 0


class FraudAnalysisResponse(BaseModel):
    order_id: int
    is_flagged: bool
    risk_score: float