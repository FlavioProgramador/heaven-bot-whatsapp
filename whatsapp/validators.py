import hashlib
import hmac

from django.conf import settings


def validate_webhook_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Validate Meta X-Hub-Signature-256 against the configured app secret."""
    secret = settings.WHATSAPP_APP_SECRET
    if not secret or not signature_header:
        return False
    algorithm, separator, supplied_digest = signature_header.partition("=")
    if separator != "=" or algorithm.lower() != "sha256" or not supplied_digest:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, supplied_digest)
