from django.test import TestCase

from contacts.models import Contact
from whatsapp.models import MessageLog


class MessageLogTests(TestCase):
    def test_external_message_id_is_unique(self):
        contact = Contact.objects.create(phone_number="5521999999999")
        MessageLog.objects.create(external_message_id="wamid.123", contact=contact, direction=MessageLog.Direction.INBOUND)
        with self.assertRaises(Exception):
            MessageLog.objects.create(external_message_id="wamid.123", contact=contact, direction=MessageLog.Direction.INBOUND)
