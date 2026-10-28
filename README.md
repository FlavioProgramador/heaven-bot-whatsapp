# Heaven Bot WhatsApp

Robô determinístico de atendimento inicial do Heaven com Python, Django, PostgreSQL e a API oficial WhatsApp Business Platform (Cloud API). Não usa IA, automação do WhatsApp Web ou provedor intermediário.

## Estado
A base contém modelos para categorias, cursos, horários, contatos, mensagens e configuração institucional; Django Admin; integração inicial com a Cloud API; webhook GET/POST com verificação do desafio e assinatura HMAC; testes e workflow de CI.

**Ainda requer validação antes de produção.** Nenhuma credencial real foi incluída e nenhum número comercial foi alterado.

## Instalação no Windows (PowerShell)
1. Instale Python e PostgreSQL e confirme:
   ```powershell
   py --version
   psql --version
   ```
2. No PostgreSQL, crie o banco e usuário:
   ```sql
   CREATE USER heaven_bot WITH PASSWORD 'substitua-por-uma-senha-forte';
   CREATE DATABASE heaven_bot OWNER heaven_bot;
   ```
3. Na pasta do projeto:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```
4. Configure `DATABASE_URL` e `DJANGO_SECRET_KEY` no `.env`. Codifique caracteres reservados da senha para URL. Gere uma chave com:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   Mantenha `DJANGO_DEBUG=True` somente localmente.
5. Execute:
   ```powershell
   python manage.py check
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py test
   python manage.py runserver
   ```
6. Acesse `http://127.0.0.1:8000/admin/` e cadastre dados oficiais do Heaven. Não há cursos, preços ou endereço fictícios pré-cadastrados.

## WhatsApp Cloud API
Configure no `.env`: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET` e `WHATSAPP_API_VERSION`. Não versione credenciais.

Configure callback HTTPS `https://SEU_HOST/webhooks/whatsapp/`. O GET usa o verify token; o POST valida `X-Hub-Signature-256` usando o corpo bruto e o App Secret. Comece pelo número de teste da Meta. Não altere nem migre o número comercial real sem autorização explícita. Um túnel local só serve para testes, não para produção.

## Atendimento
- O menu usa categorias e cursos ativos cadastrados.
- Preço ausente é mostrado como “a confirmar”; horário não significa vaga garantida.
- Localização só aparece quando a equipe cadastra endereço/link.
- Pedido de atendimento humano pausa respostas automáticas até a equipe reativar o contato no Admin.
- `0` ou `MENU` retorna ao menu, exceto durante atendimento humano.
- A primeira versão não sincroniza mensagens enviadas manualmente pelo aplicativo WhatsApp Business nem fornece uma interface de chat para atendentes.

## Testes
Execute `python manage.py test`. Testes não devem enviar mensagens reais. O workflow no GitHub Actions executa a checagem Django e os testes quando a branch de implementação receber novos commits.

## Limitações antes da produção
A integração é síncrona. Após falha/timeout de envio, eventos duplicados não são reenviados cegamente, para evitar mensagens duplicadas; é necessário implementar reconciliação/retentativa segura (por exemplo, uma transactional outbox). Revise a seleção de cursos no menu, política de retenção de dados pessoais, logs, permissões, HTTPS e regras de janela de atendimento. O custo depende dos termos vigentes da Meta e de eventual hospedagem/túnel; não há garantia universal de custo zero ou disponibilidade 24/7 num PC pessoal.