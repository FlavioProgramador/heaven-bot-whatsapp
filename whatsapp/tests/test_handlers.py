import hashlib
import hmac
import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from contacts.models import Contact
from courses.models import Category, Course, Schedule
from whatsapp.models import MessageLog


class MenuServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Música")
        Course.objects.create(name="Violão", category=self.category, price="100.00", billing_unit=Course.BillingUnit.MONTHLY)

    @patch("whatsapp.handlers.send_text_message", return_value="wamid.out-1")
    def test_inbound_message_is_processed_and_reply_sent(self, send_message):
        from whatsapp.handlers import process_inbound_message_event

        process_inbound_message_event({"id": "wamid.in-1", "from": "5521999999999", "type": "text", "text": {"body": "1"}})
        self.assertTrue(send_message.called)
        self.assertTrue(MessageLog.objects.filter(external_message_id="wamid.in-1", direction="inbound").exists())
        self.assertTrue(MessageLog.objects.filter(external_message_id="wamid.out-1", direction="outbound").exists())

    @patch("whatsapp.handlers.send_text_message", return_value="wamid.out-2")
    def test_duplicate_message_does_not_send_duplicate_reply(self, send_message):
        from whatsapp.handlers import process_inbound_message_event

        message = {"id": "wamid.same", "from": "5521999999999", "type": "text", "text": {"body": "MENU"}}
        process_inbound_message_event(message)
        process_inbound_message_event(message)
        self.assertEqual(send_message.call_count, 1)

    @patch("whatsapp.handlers.send_text_message", return_value="wamid.out-3")
    def test_human_handoff_pauses_automation(self, send_message):
        from whatsapp.handlers import process_inbound_message_event

        process_inbound_message_event({"id": "wamid.in-handoff", "from": "5521999999999", "type": "text", "text": {"body": "4"}})
        contact = Contact.objects.get(phone_number="5521999999999")
        self.assertTrue(contact.human_handoff_active)
        before = send_message.call_count
        process_inbound_message_event({"id": "wamid.in-paused", "from": "5521999999999", "type": "text", "text": {"body": "MENU"}})
        self.assertEqual(send_message.call_count, before)


@override_settings(WHATSAPP_VERIFY_TOKEN="test-verify", WHATSAPP_APP_SECRET="test-app-secret")
class WebhookViewTests(TestCase):
    def sign(self, body):
        digest = hmac.new(b"test-app-secret", body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def test_verification_challenge_success(self):
        response = self.client.get("/webhooks/whatsapp/", {
            "hub.mode": "subscribe", "hub.verify_token": "test-verify", "hub.challenge": "12345"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "12345")

    def test_verification_challenge_failure(self):
        response = self.client.get("/webhooks/whatsapp/", {
            "hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "12345"
        })
        self.assertEqual(response.status_code, 403)

    @patch("whatsapp.handlers.send_text_message", return_value="wamid.out")
    def test_signed_message_payload(self, send_message):
        body = json.dumps({
            "object": "whatsapp_business_account",
            "entry": [{"changes": [{"value": {
                "contacts": [{"profile": {"name": "Teste"}}],
                "messages": [{"id": "wamid.webhook", "from": "5521999999999", "type": "text", "text": {"body": "MENU"}}]
            }}]}]
        }).encode()
        response = self.client.post("/webhooks/whatsapp/", data=body, content_type="application/json", HTTP_X_HUB_SIGNATURE_256=self.sign(body))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(send_message.called)

    def test_invalid_signature_is_rejected(self):
        response = self.client.post("/webhooks/whatsapp/", data=b'{"object":"whatsapp_business_account"}', content_type="application/json", HTTP_X_HUB_SIGNATURE_256="sha256=bad")
        self.assertEqual(response.status_code, 401)
