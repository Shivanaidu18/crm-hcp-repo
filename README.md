# AI-First CRM - HCP Log Interaction Module

AI-driven CRM interaction logger for pharmaceutical field reps. The app uses a split-screen layout:

- Left panel: structured HCP interaction form
- Right panel: AI assistant chat that controls the form

The core requirement is enforced in the UI: the main interaction fields are not manually filled by the user. The AI assistant drives population and targeted edits through LangGraph tools.

## What This Demo Shows

- AI-first form population through chat
- Targeted field edits through chat
- LangGraph agent with 5 tools
- Stored interaction retrieval from the backend
- Form identity with editable `form_name` and generated `interaction_uid`
- Missing field detection
- Auto date normalization
- Multi-turn context passed into the backend
- Follow-up suggestions with priority and next follow-up date
- HCP typo correction such as "Did you mean Dr. Priya Mehta?"
- Field highlight animation when AI updates the form

## Current Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Redux Toolkit, Axios, CRA |
| Backend | FastAPI, SQLAlchemy |
| Agent | LangGraph |
| LLM | Groq `llama-3.3-70b-versatile` |
| Database | PostgreSQL with SQLite fallback |

## Architecture

```text
React + Redux
  -> ChatPanel sends messages + current form state
  -> FastAPI /api/chat
  -> LangGraph tool routing
  -> tool result mapped back into Redux form state
  -> Form auto-updates on the left panel

FastAPI /api/interactions
  -> SQLAlchemy Interaction model
  -> PostgreSQL if available
  -> SQLite fallback if Postgres connection fails
```

## LangGraph Tools

The backend implements 5 tools in [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py):

1. `log_interaction`
   Extracts structured CRM fields from natural language and populates the form.

2. `edit_interaction`
   Updates only the requested fields without overwriting the rest of the form.

3. `suggest_followup`
   Produces AI follow-up suggestions, priority, and next follow-up date.

4. `search_hcp`
   Searches known HCP records and supports typo-aware correction.

5. `analyze_sentiment`
   Infers interaction sentiment and can update the sentiment field.

## Key Frontend Behavior

- Main form fields are read-only and AI-controlled
- `form_name` is editable manually and can also be updated through AI chat
- `interaction_uid` is assigned on save
- Stored interactions can be loaded back into the form
- User and assistant chat history are visible in the right panel
- Updated fields glow to show exactly what changed

Main UI files:

- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\InteractionForm.jsx](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\InteractionForm.jsx)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\ChatPanel.jsx](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\ChatPanel.jsx)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\store\interactionSlice.js](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\store\interactionSlice.js)

## Backend Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/chat` | AI assistant entry point |
| POST | `/api/interactions` | Save interaction |
| GET | `/api/interactions` | List stored interactions |
| GET | `/api/interactions/{id}` | Load one stored interaction |
| PUT | `/api/interactions/{id}` | Update an interaction |
| GET | `/api/hcps/search?q=` | Search HCPs |
| GET | `/health` | Health check |

## Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Groq API key
- PostgreSQL optional but recommended

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/crm_hcp
CORS_ORIGINS=http://localhost:3000
```

Run:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm start
```

Frontend:

- [http://localhost:3000](http://localhost:3000)

Backend:

- [http://localhost:8000](http://localhost:8000)
- [http://localhost:8000/docs](http://localhost:8000/docs)

## Database Notes

The backend tries `DATABASE_URL` first. If that connection fails, it falls back to:

- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\crm_hcp.sqlite3](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\crm_hcp.sqlite3)

This fallback keeps the app demo-able even if local Postgres is misconfigured.

## Example Prompts

Use these in the chat panel:

1. `Met Dr. Smith today, discussed Product X efficacy, positive sentiment, shared brochures`
2. `Change only the sentiment to Negative`
3. `Add follow-up action: schedule a call next Friday`
4. `Suggest follow-up actions for this interaction`
5. `Search for Dr. Priya Mehta`
6. `Rename this form to Apollo oncology follow-up`

## Project Structure

```text
crm-hcp/
|-- backend/
|   |-- agent.py
|   |-- database.py
|   |-- main.py
|   |-- requirements.txt
|   |-- crm_hcp.sqlite3
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |   |-- ChatPanel.jsx
|   |   |   |-- InteractionForm.jsx
|   |   |-- services/
|   |   |   |-- api.js
|   |   |-- store/
|   |   |   |-- interactionSlice.js
|
|-- docker-compose.yml
|-- README.md
```

## Submission Notes

- Uses LangGraph, not hard-coded-only routing
- Uses Groq with `llama-3.3-70b-versatile`
- Enforces AI-driven form entry for the main interaction fields
- Demonstrates at least 5 tools as required
- Supports storing and reloading prior interaction flows

## Demo Script

For a ready-to-record evaluator walkthrough, use:

- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\DEMO_SCRIPT.md](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\DEMO_SCRIPT.md)

## Workflow Structure

The end-to-end workflow is:

1. User enters a natural-language request in the chat panel
2. Frontend sends chat history and current form state to `/api/chat`
3. Backend routes the request through the LangGraph agent
4. Agent selects the appropriate tool
5. Tool returns structured CRM data
6. Backend returns the tool result to the frontend
7. Redux updates the form state
8. UI highlights changed fields and shows missing fields if needed
9. User can save the interaction to persistent storage
10. Saved interactions can be reloaded into the form later

### Workflow Diagram

```mermaid
flowchart TD
    A["User enters chat prompt"] --> B["ChatPanel sends messages + current form"]
    B --> C["FastAPI /api/chat"]
    C --> D["LangGraph agent"]
    D --> E{"Route to tool"}
    E --> F["log_interaction"]
    E --> G["edit_interaction"]
    E --> H["suggest_followup"]
    E --> I["search_hcp"]
    E --> J["analyze_sentiment"]
    F --> K["Structured tool result"]
    G --> K
    H --> K
    I --> K
    J --> K
    K --> L["Frontend receives tool_result"]
    L --> M["Redux updates interaction state"]
    M --> N["Interaction form updates"]
    M --> O["Field highlight + missing field indicators"]
    N --> P["User saves interaction"]
    P --> Q["FastAPI /api/interactions"]
    Q --> R["PostgreSQL or SQLite fallback"]
    R --> S["Stored interactions list"]
    S --> T["User reloads a saved interaction"]
```

## UML Diagram

```mermaid
classDiagram
    class User {
      +enterPrompt()
      +reviewForm()
      +saveInteraction()
      +loadStoredInteraction()
    }

    class ChatPanel {
      +sendMessage()
      +renderMessages()
    }

    class InteractionForm {
      +renderForm()
      +loadStoredItems()
      +handleSave()
      +handleLoadInteraction()
    }

    class ReduxStore {
      +interactionState
      +chatState
      +updateFields()
      +hydrateInteraction()
    }

    class FastAPI {
      +POST /api/chat
      +POST /api/interactions
      +GET /api/interactions
      +GET /api/interactions/{id}
      +PUT /api/interactions/{id}
      +GET /health
    }

    class LangGraphAgent {
      +run_agent()
      +route_tool_call()
      +agent_node()
    }

    class Tools {
      +log_interaction()
      +edit_interaction()
      +suggest_followup()
      +search_hcp()
      +analyze_sentiment()
    }

    class DatabaseLayer {
      +Interaction
      +HCP
      +create_tables()
      +resolve_engine()
    }

    class PostgreSQL {
      +primary persistence
    }

    class SQLite {
      +fallback persistence
    }

    User --> ChatPanel
    User --> InteractionForm
    ChatPanel --> ReduxStore
    ChatPanel --> FastAPI
    InteractionForm --> ReduxStore
    InteractionForm --> FastAPI
    FastAPI --> LangGraphAgent
    LangGraphAgent --> Tools
    FastAPI --> DatabaseLayer
    DatabaseLayer --> PostgreSQL
    DatabaseLayer --> SQLite
    ReduxStore --> InteractionForm
    ReduxStore --> ChatPanel
```
