from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app.schemas import FraudAnalysisRequest, FraudAnalysisResponse
from app.services import FraudChecker


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "ml_models" / "fraud_check_model" / "fraud_model.joblib"
SCALER_PATH = BASE_DIR / "ml_models" / "fraud_check_model" / "scaler.joblib"

ml_models = {}

@asynccontextmanager
async def lifespan(_app: FastAPI):
    ml_models["fraud_checker"] = FraudChecker(
        model_path=str(MODEL_PATH),
        scaler_path=str(SCALER_PATH),
    )
    yield
    ml_models.clear()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    @app.get("/", include_in_schema=False)
    def home():
        return RedirectResponse(url="/docs")


    @app.post("/check_fraud", response_model=FraudAnalysisResponse, name="check_fraud")
    def check_fraud(payload: FraudAnalysisRequest):
        return ml_models["fraud_checker"].predict(payload)

    return app

app = create_app()