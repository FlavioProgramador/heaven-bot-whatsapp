# Heaven Bot WhatsApp

Robô determinístico de atendimento inicial pelo WhatsApp para o Heaven, desenvolvido com Python, Django e PostgreSQL, usando a API oficial WhatsApp Business Platform (Cloud API).

> **Status:** documentação inicial. A integração com a Meta depende de configuração e credenciais fornecidas pelo responsável. Nenhum número comercial foi alterado.

## Objetivo

Permitir que clientes consultem modalidades, cursos, preços, horários e localização, ou solicitem atendimento humano. Nesta versão não há IA, LLM ou provedor intermediário.

## Escopo planejado

- [ ] Projeto Django modular
- [ ] Persistência PostgreSQL e migrações
- [ ] Administração de categorias, cursos, horários e informações institucionais
- [ ] Máquina de estados determinística para o atendimento
- [ ] Webhook com validação de desafio e assinatura
- [ ] Envio de mensagens pela Cloud API
- [ ] Idempotência e registro técnico de mensagens
- [ ] Testes automatizados sem chamadas externas reais
- [ ] Guia de instalação no Windows/PowerShell
- [ ] Checklist para configurar a Meta e habilitar o número comercial

## Princípios e limites

- Usar somente a API oficial da Meta; não automatizar WhatsApp Web.
- Não inventar preços, horários, endereço ou disponibilidade.
- Não armazenar segredos no Git.
- Não enviar mensagens de campanha ou proativas.
- Solicitar autorização explícita antes de migrar ou alterar o número real.
- O Django Admin será a interface inicial de administração; não haverá frontend independente nesta etapa.

## Tecnologias previstas

- Python
- Django
- PostgreSQL
- Requisições HTTP à WhatsApp Cloud API
- Variáveis de ambiente para configuração

As versões exatas e dependências serão registradas nos arquivos do projeto durante a implementação.

## Configuração

Consulte o arquivo `.env.example` (quando disponibilizado) para os nomes das variáveis de ambiente. Não compartilhe nem versione tokens de acesso, App Secret, senhas ou dados pessoais.

O webhook da Meta precisa estar acessível por HTTPS. Um túnel local pode ser útil durante testes, mas não substitui infraestrutura de produção; o robô só fica disponível enquanto o backend está em execução.

## Dados institucionais

Os dados oficiais do Heaven (cursos, preços, horários, endereço e contato humano) devem ser cadastrados pela equipe responsável no painel administrativo. Nenhum dado comercial fictício deve ser tratado como real.

## Desenvolvimento

A documentação de instalação para Windows, comandos, testes, configuração do PostgreSQL e etapas da Meta será ampliada junto com a implementação do código.
