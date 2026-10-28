import json
import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .handlers import process_webhook_payload
from .validators import validate_webhook_signature

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode", "")
        token = request.GET.get("hub.verify_token", "")
        challenge = request.GET.get("hub.challenge", "")
        if (
            mode == "subscribe"
            and settings.WHATSAPP_VERIFY_TOKEN
            and token == settings.WHATSAPP_VERIFY_TOKEN
            and challenge
        ):
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponse("Verificação inválida", status=403, content_type="text/plain")

    if len(request.body) > settings.WHATSAPP_WEBHOOK_MAX_BODY_BYTES:
        return JsonResponse({"error": "Payload muito grande."}, status=413)
    if not validate_webhook_signature(request.body, request.headers.get("X-Hub-Signature-256")):
        logger.warning("WhatsApp webhook signature validation failed")
        return JsonResponse({"error": "Assinatura inválida."}, status=401)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Payload JSON inválido."}, status=400)
    if not isinstance(payload, dict) or payload.get("object") != "whatsapp_business_account":
        return JsonResponse({"error": "Evento inválido."}, status=400)

    try:
        process_webhook_payload(payload)
    except Exception:
        logger.exception("WhatsApp webhook processing failed")
        return JsonResponse({"error": "Falha ao processar evento."}, status=500)
    return JsonResponse({"status": "ok"})
