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

Required environment variables are loaded from `.env` in the project root:

- `FLEXOPUS_API_TOKEN`
- `FLEXOPUS_API_URL`
- `GOOGLE_API_KEY`
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

Start both services together with Docker Compose:

```bash
docker compose up --build
```

When using Docker Compose, the UI talks to the API service by name (`http://api:8000/api`), so no
host override is needed.

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