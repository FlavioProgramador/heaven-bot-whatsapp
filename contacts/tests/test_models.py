from django.test import TestCase

from contacts.models import Contact


class ContactTests(TestCase):
    def test_contact_defaults_to_main_menu(self):
        contact = Contact.objects.create(phone_number="5521999999999")
        self.assertEqual(contact.conversation_state, Contact.ConversationState.MAIN_MENU)
        self.assertFalse(contact.human_handoff_active)

    def test_phone_number_must_be_unique(self):
        Contact.objects.create(phone_number="5521999999999")
        with self.assertRaises(Exception):
            Contact.objects.create(phone_number="5521999999999")
