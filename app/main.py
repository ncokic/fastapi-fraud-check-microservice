from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.config import settings
from app.schemas import FraudAnalysisRequest, FraudAnalysisResponse
from app.services import FraudCheckerService


ml_models = {}

@asynccontextmanager
async def lifespan(_app: FastAPI):
    ml_models["fraud_checker"] = FraudCheckerService(
        model_path=settings.model_path,
        scaler_path=settings.scaler_path,
    )
    yield
    ml_models.clear()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="FastAPI Fraud Check Microservice")

    @app.get("/", include_in_schema=False)
    def home():
        return RedirectResponse(url="/docs")


    @app.post("/check_fraud", response_model=FraudAnalysisResponse, name="check_fraud")
    def check_fraud(payload: FraudAnalysisRequest):
        return ml_models["fraud_checker"].predict(payload)

    return app

app = create_app()