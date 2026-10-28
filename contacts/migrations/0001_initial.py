from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_number", models.CharField(db_index=True, max_length=20, unique=True, verbose_name="telefone normalizado")),
                ("name", models.CharField(blank=True, max_length=160, verbose_name="nome")),
                ("conversation_state", models.CharField(choices=[("MENU_PRINCIPAL","Menu principal"),("LISTANDO_CATEGORIAS","Listando categorias"),("LISTANDO_CURSOS","Listando cursos"),("CONSULTANDO_CURSO","Consultando curso"),("CONSULTANDO_HORARIOS","Consultando horários"),("ATENDIMENTO_HUMANO","Atendimento humano")], default="MENU_PRINCIPAL", max_length=32, verbose_name="estado da conversa")),
                ("human_handoff_active", models.BooleanField(db_index=True, default=False, verbose_name="atendimento humano ativo")),
                ("first_contact_at", models.DateTimeField(auto_now_add=True, verbose_name="primeiro contato")),
                ("last_contact_at", models.DateTimeField(auto_now=True, verbose_name="último contato")),
            ],
            options={"verbose_name":"contato","verbose_name_plural":"contatos","ordering":["-last_contact_at"]},
        ),
    ]
