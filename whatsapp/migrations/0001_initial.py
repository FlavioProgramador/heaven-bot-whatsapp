from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("contacts","0001_initial")]
    operations = [
        migrations.CreateModel(
            name="MessageLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_message_id", models.CharField(blank=True, max_length=180, null=True, unique=True, verbose_name="ID externo da mensagem")),
                ("direction", models.CharField(choices=[("inbound","Recebida"),("outbound","Enviada")], max_length=10, verbose_name="direção")),
                ("message_type", models.CharField(default="text", max_length=40, verbose_name="tipo")),
                ("processing_status", models.CharField(choices=[("received","Recebida"),("processed","Processada"),("sent","Enviada"),("failed","Falhou"),("ignored","Ignorada")], default="received", max_length=16, verbose_name="status técnico")),
                ("error_code", models.CharField(blank=True, max_length=80, verbose_name="código de erro")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="data e hora")),
                ("processed_at", models.DateTimeField(blank=True, null=True, verbose_name="processada em")),
                ("contact", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="messages", to="contacts.contact")),
            ],
            options={"verbose_name":"registro de mensagem","verbose_name_plural":"registros de mensagens","ordering":["-created_at"]},
        ),
    ]
