# Flexopus 4.7

Flexopus 4.7 is a chat application for exploring Flexopus booking data with an LLM-backed assistant.
It combines a FastAPI backend, LangChain tools, and a Streamlit UI so users can ask questions about
buildings, locations, bookables, bookings, and user records.

## Disclaimer

This is an **unofficial, non-commercial hobby project**, built for fun and to explore LLM agents
on top of a real-world booking API. It is **not affiliated with, endorsed by, or sponsored by
Flexopus** in any way. "Flexopus" and any related names, logos, and trademarks are the property of
their respective owner(s) and are used here only to describe the product this project integrates
with.

The code is provided free of charge, "as is", without warranty of any kind, and is not intended
for commercial or production use. Use at your own risk, and bring your own Flexopus/Gemini
credentials.

## About Flexopus

[Flexopus](https://flexopus.com) is a third-party workplace-management platform for booking desks,
rooms, and other shared resources across buildings and locations. This project talks to a
Flexopus instance's public API to let a chat assistant answer questions and make bookings on a
user's behalf - it does not modify, replace, or resell any part of Flexopus itself.

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

## How to Run

The project uses Python 3.13.

### Configuration

The UI asks each user for their Flexopus API key, Flexopus URL, and Gemini API key at the start of
the session, so those three don't need to live in `.env`. Environment variables loaded from `.env`
in the project root are just local-dev fallbacks and tracing config:

- `FLEXOPUS_API_TOKEN` (fallback if not supplied in the session form)
- `FLEXOPUS_API_URL` (fallback if not supplied in the session form)
- `GOOGLE_API_KEY` (fallback if not supplied in the session form)
- `LANGSMITH_TRACING`
- `LANGSMITH_ENDPOINT`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`

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

Each service has its own Dockerfile at the repo root and listens on `$PORT` (defaulting to
`8080`). Build and run them independently:

```bash
docker build -f Dockerfile.api -t flexopus-api .
docker run --env-file .env -p 8000:8080 flexopus-api
```

```bash
docker build -f Dockerfile.streamlit -t flexopus-ui .
docker run --env-file .env -e BACKEND_API_URL=http://host.docker.internal:8000/api -p 8501:8080 flexopus-ui
```

### Deploying to Cloud Run (GCP)

Both Dockerfiles build and run as-is with `gcloud run deploy`, e.g.:

```bash
gcloud run deploy flexopus-api --source . --dockerfile Dockerfile.api
gcloud run deploy flexopus-ui --source . --dockerfile Dockerfile.streamlit
```

Each Cloud Run service gets its own URL, so after the API service is deployed, set
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
