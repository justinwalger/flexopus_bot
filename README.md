# Flexopus 4.7

Flexopus 4.7 is a chat application for exploring Flexopus booking data with an LLM-backed assistant.
It combines a FastAPI backend, LangChain tools, and a Streamlit UI so users can ask questions about
buildings, locations, bookables, bookings, and user records.

## What It Does

- Answers questions about Flexopus resources in natural language.
- Streams assistant responses into the UI.
- Supports human-in-the-loop approval for selected tool calls.
- Exposes multiple Flexopus API tools for buildings, locations, occupancy, availability, and users.

## Project Layout

- `src/api`: FastAPI app, request/response schemas, and route handlers.
- `src/application`: application-level services that orchestrate the conversation flow.
- `src/llm`: agent setup, prompts, state helpers, and Flexopus tool implementations.
- `src/ui`: Streamlit frontend, chat rendering, and backend API client.

## Local Setup

The project uses Python 3.13.

The UI now asks each user for their Flexopus API key, Flexopus URL, and Gemini API key at the start
of the session, so those three no longer need to live in `.env`. Environment variables loaded from
`.env` in the project root are now just local-dev fallbacks and tracing config:

- `FLEXOPUS_API_TOKEN` (fallback if not supplied in the session form)
- `FLEXOPUS_API_URL` (fallback if not supplied in the session form)
- `GOOGLE_API_KEY` (fallback if not supplied in the session form)
- `LANGSMITH_TRACING`
- `LANGSMITH_ENDPOINT`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`


## Running the App

### Local Run

Install the dependency groups first:

```bash
uv sync --locked --group api --group ui
```

Start the backend from `src/api`:

```bash
cd src/api
uv run fastapi dev main.py
```

Start the UI from `src/ui`:

```bash
cd src/ui
uv run streamlit run app.py
```

### Docker Build and Run

The API and UI are split into separate Compose files (`docker-compose.api.yml` and
`docker-compose.ui.yml`) so each service can be built, run, and deployed independently. They
communicate over a shared external Docker network, which needs to be created once:

```bash
docker network create flexopus-network
```

Start the API:

```bash
docker compose -f docker-compose.api.yml up --build
```

Start the UI:

```bash
docker compose -f docker-compose.ui.yml up --build
```

Since both services join the shared `flexopus-network`, the UI can still reach the API by service
name (`http://api:8080/api`), no host override needed. The API is published on host port `8000` and
the UI on host port `8501`; both containers listen internally on `8080`.

### Deploying to Cloud Run (GCP)

`Dockerfile.api` and `Dockerfile.streamlit` each listen on `$PORT` (defaulting to `8080`), so they
build and run as-is with `gcloud run deploy`, e.g.:

```bash
gcloud run deploy flexopus-api --source . --dockerfile Dockerfile.api
gcloud run deploy flexopus-ui --source . --dockerfile Dockerfile.streamlit
```

Cloud Run doesn't share the Docker Compose network, so after the API service is deployed, set
`BACKEND_API_URL` on the UI service to the API's actual Cloud Run URL:

```bash
gcloud run services update flexopus-ui \
  --set-env-vars BACKEND_API_URL=https://flexopus-api-<hash>.a.run.app/api
```

## Tooling

The agent currently includes tools for:

- listing buildings and groups
- searching users by email
- exporting all users as CSV
- listing bookings for buildings, locations, and bookables
- checking location occupancy
- checking bookable availability

Tool responses are typed with Pydantic models where the payload shape is stable enough to benefit from it.

## Human-in-the-Loop

Some tools can be paused for manual approval before they run.
When that happens, the UI shows the pending tool name and arguments, and you can approve or reject the action.

## Notes

- The UI keeps a `thread_id` per session so tool approvals can resume the same run.
- The project uses Ruff for linting and import sorting with a 100 character line length.


## TODOS
- Deploy to hyperscaler
- Check docker
- Terraform setup
- Add POST functionality
- possiblity to create visualizations
- possibility to export reports
- add eval
- add tests
- subagents etc
- auth