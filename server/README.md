# School SaaS AI Agent API

FastAPI exposes the existing LangGraph agent to the client. The graph classifies
each question, routes it to the relevant knowledge source(s), and generates a
final answer.

## Run locally

From the `server/` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env_example .env
```

Add the API keys for the sources you want to use to `.env`, then start the API:

```bash
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Endpoints

- `GET /health` — reports API liveness and available provider/model choices.
- `POST /api/chat` — runs a question through the agent.

Example request:

```json
{
  "query": "How do I add a student?",
  "provider": "gemini",
  "model": "gemini-3.5-flash-lite"
}
```

Example response:

```json
{
  "answer": "..."
}
```

The health response includes `ai_provider`, `ai_model`, and `ai_configured`
for the default selection, along with a `providers` catalog. Providers without
server-side API keys are marked unconfigured. Chat requests may select a
provider and model from this catalog; the API validates the selection against
an allowlist. API keys are never sent to the client. The health endpoint
reports local configuration only; it does not test provider availability.

Queries must contain 1–2000 non-whitespace characters.

## AI model and request timing

The agent supports Google Gemini and Groq. Configure `GEMINI_API_KEY` and/or
`GROQ_API_KEY` on the server. `GEMINI_MODEL` and `GROQ_MODEL` set each
provider's default model; only the models in the health catalog are accepted.
Audio transcription and safety-classification models are listed for reference
but disabled for chat until their dedicated workflows are implemented.
Each model call uses a 20-second timeout and one retry. Backend logs report the
classifier, generation, and total graph durations. A single-source
general-knowledge answer is returned directly instead of being sent through a
second generation call.

## Tenant data

The chat request does not accept a tenant or branch identifier. The current
project does not yet include authentication, so the API cannot safely establish
which school's records a caller may access. School-database requests therefore
fail closed until trusted tenant context is provided by a future authentication
layer. The JSON seed data is for local development only.
