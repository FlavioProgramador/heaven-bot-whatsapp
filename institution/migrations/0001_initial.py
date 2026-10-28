from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="InstitutionSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="Heaven", max_length=160, verbose_name="nome do estabelecimento")),
                ("address", models.TextField(blank=True, verbose_name="endereço")),
                ("google_maps_url", models.URLField(blank=True, verbose_name="link do Google Maps")),
                ("human_support_phone", models.CharField(blank=True, max_length=20, verbose_name="telefone de atendimento humano")),
                ("opening_hours", models.TextField(blank=True, verbose_name="horário de funcionamento")),
                ("welcome_message", models.TextField(default="Olá! Seja bem-vindo ao Heaven!\n\nComo podemos ajudar?", verbose_name="mensagem de boas-vindas")),
                ("closing_message", models.TextField(blank=True, verbose_name="mensagem de encerramento")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
            ],
            options={"verbose_name":"configuração institucional","verbose_name_plural":"configurações institucionais"},
        ),
    ]
