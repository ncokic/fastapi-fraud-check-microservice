import hashlib
import hmac
import json
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.config import settings

CUSTOM_PAYLOAD = {
    "order_id": 10,
    "user_id": 5,
    "order_amount": 15.99,
    "orders_last_24h": 1,
    "is_shipping_billing_mismatch": False,
    "shipping_country": "RS",
    "ip_country": "RS",
    "account_age_min": 5000
}


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


if __name__ == "__main__":
    print(f"HMAC Signature: {generate_hmac_signature(CUSTOM_PAYLOAD)}")