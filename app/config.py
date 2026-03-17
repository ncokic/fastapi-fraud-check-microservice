from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    SIGNATURE_SECRET_KEY: str
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.3

    @property
    def model_path(self) -> str:
        return str(self.BASE_DIR / "app" / "ml_models" / "fraud_check_model" / "fraud_model.joblib")

    @property
    def scaler_path(self) -> str:
        return str(self.BASE_DIR / "app" / "ml_models" / "fraud_check_model" / "scaler.joblib")


settings = Settings() # type: ignore[call-arg]