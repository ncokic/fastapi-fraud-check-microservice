import hashlib
import hmac
import json

from app.config import settings


def generate_hmac_signature(payload):
    secret_key = settings.SIGNATURE_SECRET_KEY
    normalized_payload = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True
    )

    signature = hmac.new(
        key=secret_key.encode(),
        msg=normalized_payload.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return signature