# Heaven Bot WhatsApp

Robô determinístico de atendimento inicial do Heaven usando Python, Django, PostgreSQL e a API oficial WhatsApp Business Platform (Cloud API). Não usa IA, automação do WhatsApp Web ou provedores intermediários.

## Estado do projeto
O repositório contém a base do projeto Django, modelos de categorias, cursos, horários, contatos, logs de mensagens e configurações institucionais, administração Django, serviço HTTP inicial da Cloud API, webhook com desafio GET e validação HMAC SHA-256 em POST, menu por regras e testes iniciais.

**Antes de produção:** executar testes, validar credenciais Meta de teste e revisar idempotência/retentativas, logs e retenção de dados pessoais, segurança e janela de atendimento. Nenhuma credencial real foi adicionada nem número comercial alterado.

## Instalação no Windows (PowerShell)
1. Instale Python e PostgreSQL; confirme:
   ```powershell
   py --version
   psql --version
   ```
2. Crie o usuário e o banco PostgreSQL:
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
4. Configure `DATABASE_URL` no `.env`. Codifique caracteres especiais da senha para URL. Gere a chave:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   Use o resultado em `DJANGO_SECRET_KEY`. Mantenha DEBUG ligado somente no ambiente local.
5. Execute:
   ```powershell
   python manage.py check
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py test
   python manage.py runserver
   ```
6. Acesse `http://127.0.0.1:8000/admin/` e cadastre apenas dados oficiais do Heaven.

## WhatsApp Cloud API
Configure em `.env`: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET`, `WHATSAPP_API_VERSION`. Nunca versione segredos.

Configure callback HTTPS `https://SEU_HOST/webhooks/whatsapp/`. O GET valida o verify token; o POST valida `X-Hub-Signature-256` usando o corpo bruto e o App Secret. Comece pelo número de teste Meta. Não migre o número comercial real sem autorização explícita. Túnel local serve para teste, mas não é infraestrutura de produção.

## Fluxo
Categorias e cursos são carregados do banco e precisam estar ativos. Preços ausentes são marcados como a confirmar. Horários são informativos e não confirmam vaga. Localização só aparece quando cadastrada. Pedido de atendimento humano pausa o robô até a equipe liberar o contato no Admin. `0` ou `MENU` volta ao menu, exceto durante atendimento humano. Não há sincronização das mensagens enviadas manualmente pelo aplicativo WhatsApp Business nem chat integrado para atendentes.

## Testes
Execute `python manage.py test`. Testes externos devem usar mocks e nunca enviar mensagens reais. A conexão GitHub usada para editar os arquivos não executa Python localmente; confirme os resultados no Windows e no CI.

## Custos e limitações
Não há IA nem intermediário no desenho. O custo depende das condições comerciais vigentes da Meta e de eventual hospedagem/túnel. O robô só funciona enquanto o backend está ativo. Falhas de envio são registradas e não repetidas cegamente; antes da produção, implemente reconciliação/retentativa segura e política documentada de retenção de logs.
