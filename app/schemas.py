from pydantic import BaseModel, Field
import enum


class FraudAnalysisRequest(BaseModel):
    order_id: int
    user_id: int
    order_amount: float = Field(gt=0)
    orders_last_24h: int = Field(gt=0)
    is_shipping_billing_mismatch: bool
    shipping_country: str = Field(min_length=2, max_length=2)
    ip_country: str = Field(min_length=2, max_length=2)
    account_age_min: int

    @property
    def is_country_mismatch(self) -> int:
        return 1 if self.shipping_country != self.ip_country else 0

    @property
    def is_address_mismatch(self) -> int:
        return 1 if self.is_shipping_billing_mismatch else 0

    @property
    def is_new_account(self) -> int:
        return 1 if self.account_age_min < 1440 else 0

    @property
    def has_high_velocity(self) -> int:
        return 1 if self.orders_last_24h > 3 else 0

    @property
    def diff_country_new_acc(self) -> int:
        return 1 if self.is_country_mismatch * self.is_new_account else 0

    @property
    def diff_country_high_vel(self) -> int:
        return 1 if self.is_country_mismatch * self.has_high_velocity else 0


class FraudAnalysisResponse(BaseModel):
    order_id: int
    risk_assessment: str
    risk_score: float
    reasons: str | list[str]