# Meu Radar Financeiro Processor

API para processamento de documentos financeiros, utilizando Docling e Supabase.

## Requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Gerenciador de pacotes)

## Configuração Local

1.  **Clone o repositório** e entre na pasta.

2.  **Configure o ambiente**:
    Copie o arquivo de exemplo e preencha as variáveis.
    ```bash
    cp .env.example .env
    ```
    Edite `.env` com suas credenciais do Supabase.

3.  **Instale as dependências**:
    ```bash
    uv sync
    ```

4.  **Rode a aplicação (Modo Desenvolvimento)**:
    Este comando ativa hot-reload e logs detalhados.
    
    Opção 1 (via arquivo):
    ```bash
    uv run fastapi dev app/main.py
    ```

    Opção 2 (via módulo - certifique-se de estar na raiz):
    ```bash
    uv run fastapi dev app.main:app
    ```

    Acesse:
    - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
    - Health Check: [http://localhost:8000/health](http://localhost:8000/health)

## Docker / Produção

O projeto conta com um `Dockerfile` otimizado para produção.

### Build

```bash
docker build -t mrf-processor .
```

### Run

Execute o container passando as variáveis de ambiente necessárias.

```bash
docker run -d \
  -p 8000:8000 \
  --name mrf-processor \
  --env-file .env \
  mrf-processor
```

### Configuração de Workers

Para ajustar o número de workers em produção (padrão: 1), você pode sobrescrever o comando:

```bash
docker run -d -p 8000:8000 --env-file .env mrf-processor uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Estrutura do Projeto

- `app/`: Pacote principal da aplicação.
  - `main.py`: Entrypoint e definição do app FastAPI.
  - `domain`: Lógica de negócio (Docling).
  - `infra`: Integrações (Supabase, Scheduler).
  - `api`: Rotas HTTP.

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `SUPABASE_URL` | URL do projeto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave de serviço (Service Role) para acesso privilegiado |
| `SUPABASE_STORAGE_BUCKET` | Nome do bucket no Storage |
