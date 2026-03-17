import hashlib
import hmac
import json
from typing import Annotated

from fastapi import Request, Header, HTTPException

from app.config import settings

SECRET_KEY = settings.SIGNATURE_SECRET_KEY


async def verify_hmac_signature(
        request: Request,
        signature: Annotated[str, Header(alias="X-Signature")]
):
    data = await request.json()
    normalized_data = json.dumps(
        data,
        separators=(",", ":"),
        sort_keys=True
    )

    expected_signature = hmac.new(
        key=SECRET_KEY.encode(),
        msg=normalized_data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(401, "Invalid signature.")

    return True