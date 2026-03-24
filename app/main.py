from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse

from app.schemas import FraudAnalysisRequest, FraudAnalysisResponse
from app.utils.security import verify_hmac_signature
from app.services import FraudCheckerService
from app.utils.error_handlers import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.fraud_checker = FraudCheckerService()
    yield
    del app.state.fraud_checker


def get_fraud_checker(request: Request):
    return request.app.state.fraud_checker


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="FastAPI Fraud Check Microservice")
    register_error_handlers(app)

    @app.get("/", include_in_schema=False)
    def home():
        return RedirectResponse(url="/docs")


    @app.post(
        "/check_fraud",
        response_model=FraudAnalysisResponse,
        name="check_fraud",
        dependencies=[Depends(verify_hmac_signature)]
    )
    def check_fraud(
            payload: FraudAnalysisRequest,
            model: Annotated[FraudCheckerService, Depends(get_fraud_checker)]
    ):
        return model.predict(payload)

    return app


app = create_app()