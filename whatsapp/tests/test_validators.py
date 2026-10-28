import hashlib
import hmac

from django.test import SimpleTestCase, override_settings

from whatsapp.validators import validate_webhook_signature


@override_settings(WHATSAPP_APP_SECRET="test-secret")
class SignatureValidationTests(SimpleTestCase):
    def test_valid_signature(self):
        body = b'{"object":"whatsapp_business_account"}'
        digest = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
        self.assertTrue(validate_webhook_signature(body, f"sha256={digest}"))

    def test_invalid_signature(self):
        self.assertFalse(validate_webhook_signature(b"{}", "sha256=not-valid"))

    @override_settings(WHATSAPP_APP_SECRET="")
    def test_missing_secret_fails_closed(self):
        self.assertFalse(validate_webhook_signature(b"{}", "sha256=abc"))
