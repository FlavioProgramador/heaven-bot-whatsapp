import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from contacts.models import Contact
from institution.models import InstitutionSettings
from .models import MessageLog

logger = logging.getLogger(__name__)


class WhatsAppConfigurationError(RuntimeError):
    pass


class WhatsAppAPIError(RuntimeError):
    pass


def _api_url(resource: str) -> str:
    version = settings.WHATSAPP_API_VERSION.strip()
    if not version:
        raise WhatsAppConfigurationError("WHATSAPP_API_VERSION não configurada.")
    return f"https://graph.facebook.com/{version}/{resource}"


def send_text_message(to: str, text: str) -> str | None:
    """Send plain text using official WhatsApp Cloud API."""
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        raise WhatsAppConfigurationError("Credenciais da Cloud API não configuradas.")
    response = requests.post(
        _api_url(f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"),
        headers={
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": text[:4000]},
        },
        timeout=(3.05, 10),
    )
    if response.status_code >= 400:
        logger.warning("WhatsApp send failed status=%s body=%s", response.status_code, response.text[:500])
        raise WhatsAppAPIError(f"A API do WhatsApp retornou HTTP {response.status_code}.")
    try:
        payload = response.json()
    except ValueError as exc:
        raise WhatsAppAPIError("Resposta JSON inválida da API do WhatsApp.") from exc
    messages = payload.get("messages") or []
    return messages[0].get("id") if messages and isinstance(messages[0], dict) else None


def institution_settings():
    return InstitutionSettings.objects.order_by("pk").first()


def menu_text() -> str:
    config = institution_settings()
    greeting = config.welcome_message.strip() if config and config.welcome_message.strip() else "Olá! Seja bem-vindo ao Heaven!"
    categories = list(
        __import__("courses.models", fromlist=["Category"]).Category.objects.filter(is_active=True).order_by("name")
    )
    choices = [f"{i} - {category.name}" for i, category in enumerate(categories, start=1)]
    option_number = len(categories) + 1
    choices.extend([
        f"{option_number} - Consultar preços e horários",
        f"{option_number + 1} - Localização",
        f"{option_number + 2} - Falar com um atendente",
    ])
    return f"{greeting}\n\nComo podemos ajudar?\n\n" + "\n".join(choices) + "\n\nDigite 0 para voltar ao menu principal."


def course_list_text(category_id: int | None = None) -> str:
    from courses.models import Course
    queryset = Course.objects.filter(is_active=True, category__is_active=True).select_related("category").order_by("name")
    if category_id is not None:
        queryset = queryset.filter(category_id=category_id)
    courses = list(queryset[:30])
    if not courses:
        return "Não encontrei cursos cadastrados nessa opção. A equipe pode confirmar as informações."
    lines = ["Cursos disponíveis:"]
    for index, course in enumerate(courses, start=1):
        lines.append(f"{index} - {course.name} ({course.category.name})")
    lines.append("\nDigite 0 para voltar ao menu principal.")
    return "\n".join(lines)


def process_inbound_message(contact: Contact, body: str) -> str | None:
    """Deterministic, stateful text-menu handler. No semantic/free-text interpretation."""
    from courses.models import Category, Course, Schedule

    normalized = (body or "").strip()
    command = normalized.upper()
    if contact.human_handoff_active or contact.conversation_state == Contact.ConversationState.HUMAN:
        return None

    if command in {"0", "MENU", "INÍCIO", "INICIO"}:
        contact.conversation_state = Contact.ConversationState.MAIN_MENU
        contact.save(update_fields=["conversation_state", "last_contact_at"])
        return menu_text()

    if command == "7":
        # Backward-compatible path if no categories have been configured.
        return _activate_human_handoff(contact)

    categories = list(Category.objects.filter(is_active=True).order_by("name"))
    count = len(categories)
    price_option = count + 1
    location_option = count + 2
    human_option = count + 3

    if command == str(human_option) or command == "ATENDENTE":
        return _activate_human_handoff(contact)

    if command == str(location_option) or command == "LOCALIZAÇÃO" or command == "LOCALIZACAO":
        config = institution_settings()
        if not config or (not config.address.strip() and not config.google_maps_url.strip()):
            return "A localização ainda não está cadastrada. A equipe pode confirmar o endereço."
        parts = ["Localização do Heaven:"]
        if config.address.strip():
            parts.append(config.address.strip())
        if config.google_maps_url.strip():
            parts.append(config.google_maps_url.strip())
        parts.append("\nDigite 0 para voltar ao menu principal.")
        return "\n".join(parts)

    if command == str(price_option) or command in {"PREÇOS", "PRECOS", "HORÁRIOS", "HORARIOS"}:
        contact.conversation_state = Contact.ConversationState.LISTING_COURSES
        contact.save(update_fields=["conversation_state", "last_contact_at"])
        return _all_course_details()

    if command.isdigit() and 1 <= int(command) <= count:
        category = categories[int(command) - 1]
        courses = list(Course.objects.filter(category=category, is_active=True).order_by("name")[:25])
        contact.conversation_state = Contact.ConversationState.LISTING_COURSES
        contact.save(update_fields=["conversation_state", "last_contact_at"])
        if not courses:
            return f"A modalidade {category.name} ainda não possui cursos cadastrados. A equipe pode confirmar."
        lines = [f"Cursos de {category.name}:"]
        for i, course in enumerate(courses, start=1):
            lines.append(f"{i} - {course.name}: {course.formatted_price()}")
        lines.append("\nDigite 0 para voltar ao menu principal.")
        return "\n".join(lines)

    # Allow selection of a course from the last ordered course list.
    if command.isdigit() and contact.conversation_state in {
        Contact.ConversationState.LISTING_COURSES,
        Contact.ConversationState.COURSE_DETAILS,
    }:
        courses = list(Course.objects.filter(is_active=True, category__is_active=True).select_related("category").order_by("category__name", "name")[:30])
        index = int(command) - 1
        if 0 <= index < len(courses):
            course = courses[index]
            schedules = list(Schedule.objects.filter(course=course, is_active=True).order_by("weekday", "starts_at")[:12])
            lines = [f"{course.name}", course.description.strip() or "Descrição ainda não cadastrada."]
            lines.append(course.formatted_price())
            lines.append(f"Frequência padrão provisória: {course.lessons_per_week} aula(s) por semana; confirme a frequência com a equipe.")
            if schedules:
                lines.append("Horários divulgados (não representam vaga confirmada):")
                lines.extend(f"- {s.get_weekday_display()}: {s.starts_at:%H:%M} às {s.ends_at:%H:%M}" for s in schedules)
            else:
                lines.append("Horários ainda não cadastrados. A equipe precisa confirmar.")
            if course.lesson_duration_minutes:
                lines.append(f"Duração: {course.lesson_duration_minutes} minutos.")
            if course.additional_information.strip():
                lines.append(course.additional_information.strip())
            lines.append("\nDigite 0 para voltar ao menu principal.")
            contact.conversation_state = Contact.ConversationState.COURSE_DETAILS
            contact.save(update_fields=["conversation_state", "last_contact_at"])
            return "\n".join(lines)

    return "Não entendi essa opção. Digite 0 para ver o menu principal ou escolha uma das opções exibidas."


def _all_course_details() -> str:
    from courses.models import Course
    courses = list(Course.objects.filter(is_active=True, category__is_active=True).select_related("category").order_by("category__name", "name")[:30])
    if not courses:
        return "Ainda não há cursos cadastrados. A equipe pode confirmar as modalidades, preços e horários."
    lines = ["Cursos, preços e horários divulgados:"]
    for course in courses:
        lines.append(f"\n{course.name} ({course.category.name})")
        lines.append(course.formatted_price())
        lines.append(f"Frequência padrão provisória: {course.lessons_per_week} aula(s) por semana; confirme a frequência com a equipe.")
        schedules = list(course.schedules.filter(is_active=True).order_by("weekday", "starts_at")[:4])
        if schedules:
            lines.extend(f"- {s.get_weekday_display()}: {s.starts_at:%H:%M} às {s.ends_at:%H:%M}" for s in schedules)
        else:
            lines.append("Horários a confirmar com a equipe.")
    lines.append("\nOs horários são informativos e não confirmam disponibilidade de vagas.")
    lines.append("Digite 0 para voltar ao menu principal.")
    return "\n".join(lines)[:3900]


def _activate_human_handoff(contact: Contact) -> str:
    contact.human_handoff_active = True
    contact.conversation_state = Contact.ConversationState.HUMAN
    contact.save(update_fields=["human_handoff_active", "conversation_state", "last_contact_at"])
    return "Sua solicitação de atendimento humano foi registrada. A equipe precisará assumir a conversa; não há confirmação de notificação ou disponibilidade imediata. Para voltar ao atendimento automático, a equipe deverá liberar o contato no painel administrativo."


def process_status_event(status_payload: dict) -> None:
    """Update technical delivery status for a matching outbound message."""
    message_id = status_payload.get("id")
    status = status_payload.get("status", "")
    if not message_id or not isinstance(status, str):
        return
    record = MessageLog.objects.filter(external_message_id=message_id, direction=MessageLog.Direction.OUTBOUND).first()
    if not record:
        return
    if status in {"sent", "delivered", "read"}:
        record.processing_status = MessageLog.ProcessingStatus.SENT
        record.error_code = ""
    elif status == "failed":
        errors = status_payload.get("errors") or []
        first_error = errors[0] if errors and isinstance(errors[0], dict) else {}
        record.processing_status = MessageLog.ProcessingStatus.FAILED
        record.error_code = str(first_error.get("code", "send_failed"))[:80]
    record.save(update_fields=["processing_status", "error_code"])
