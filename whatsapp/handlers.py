"""WhatsApp webhook payload parsing and idempotent message processing."""
import logging

from django.db import IntegrityError, transaction
from django.utils import timezone

from contacts.models import Contact
from courses.models import Category
from .models import MessageLog
from .services import process_inbound_message, process_status_event, send_text_message

logger = logging.getLogger(__name__)


def process_webhook_payload(payload: dict) -> None:
    entries = payload.get("entry", [])
    if not isinstance(entries, list):
        return
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        changes = entry.get("changes", [])
        if not isinstance(changes, list):
            continue
        for change in changes:
            if not isinstance(change, dict):
                continue
            value = change.get("value", {})
            if not isinstance(value, dict):
                continue

            statuses = value.get("statuses", [])
            if isinstance(statuses, list):
                for status in statuses:
                    if isinstance(status, dict):
                        try:
                            process_status_event(status)
                        except Exception:
                            logger.exception("Failed processing WhatsApp status event")

            messages = value.get("messages", [])
            contacts_data = value.get("contacts", [])
            if not isinstance(messages, list):
                continue
            display_name = ""
            if isinstance(contacts_data, list) and contacts_data and isinstance(contacts_data[0], dict):
                profile = contacts_data[0].get("profile", {})
                if isinstance(profile, dict):
                    display_name = str(profile.get("name", ""))[:160]

            for message in messages:
                if not isinstance(message, dict):
                    continue
                process_inbound_message_event(message, display_name)


def process_inbound_message_event(message: dict, display_name: str = "") -> None:
    message_id = message.get("id")
    sender = message.get("from")
    message_type = message.get("type", "unknown")
    if not isinstance(message_id, str) or not message_id or not isinstance(sender, str) or not sender.isdigit():
        logger.warning("Ignoring malformed WhatsApp message envelope")
        return

    # Only text commands are supported. Other message types receive a deterministic menu hint.
    body = ""
    if message_type == "text":
        text_value = message.get("text", {})
        if isinstance(text_value, dict):
            body = str(text_value.get("body", ""))[:4000]

    contact = Contact.objects.filter(phone_number=sender).first()
    if contact is None:
        contact = Contact.objects.create(phone_number=sender, name=display_name)

    try:
        with transaction.atomic():
            # Unique external ID makes Meta redelivery idempotent.
            record = MessageLog.objects.create(
                external_message_id=message_id,
                contact=contact,
                direction=MessageLog.Direction.INBOUND,
                message_type=str(message_type)[:40],
                processing_status=MessageLog.ProcessingStatus.RECEIVED,
            )
    except IntegrityError:
        logger.info("Duplicate WhatsApp inbound event ignored")
        return

    contact.last_contact_at = timezone.now()
    if display_name and not contact.name:
        contact.name = display_name
    contact.save(update_fields=["last_contact_at", "name"])

    reply = process_inbound_message(contact, body)
    if reply is None:
        record.processing_status = MessageLog.ProcessingStatus.IGNORED
        record.processed_at = timezone.now()
        record.save(update_fields=["processing_status", "processed_at"])
        return

    record.processing_status = MessageLog.ProcessingStatus.PROCESSED
    record.processed_at = timezone.now()
    record.save(update_fields=["processing_status", "processed_at"])

    try:
        sent_id = send_text_message(sender, reply)
    except Exception as exc:
        logger.exception("WhatsApp reply failed contact_suffix=%s", sender[-4:])
        record.processing_status = MessageLog.ProcessingStatus.FAILED
        record.error_code = type(exc).__name__[:80]
        record.save(update_fields=["processing_status", "error_code"])
        return

    if sent_id:
        MessageLog.objects.get_or_create(
            external_message_id=sent_id,
            defaults={
                "contact": contact,
                "direction": MessageLog.Direction.OUTBOUND,
                "message_type": "text",
                "processing_status": MessageLog.ProcessingStatus.SENT,
            },
        )
