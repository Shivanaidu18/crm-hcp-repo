# 40-Minute Elite Demo Script

This version is designed for a longer evaluator walkthrough. It is structured like a polished product + architecture presentation with a live demo in the middle, followed by a deeper technical explanation. You can present it naturally rather than reading every line word-for-word, but if you stay close to this flow, you will sound clear, confident, and very well prepared.

## Demo Goal

By the end of the session, the evaluator should clearly understand:

1. what problem this product solves
2. how the split-screen AI-first workflow works
3. why LangGraph is central to the implementation
4. how the backend, frontend, and persistence layer connect
5. how the 5 required tools are implemented and used
6. how the product behaves in real interaction scenarios
7. what extra features were added beyond the minimum requirement

---

## Suggested Time Breakdown

| Section | Time |
|---|---:|
| 1. Introduction and problem framing | 4 min |
| 2. Product overview and UX decisions | 5 min |
| 3. Live demo - primary workflow | 10 min |
| 4. Live demo - advanced scenarios | 8 min |
| 5. LangGraph architecture deep dive | 6 min |
| 6. Backend, database, and persistence | 4 min |
| 7. Wrap-up and submission summary | 3 min |

Total: about 40 minutes

---

## 1. Introduction and Problem Framing - 4 minutes

### What to say

"Hi, this is my AI-first CRM HCP interaction logging module for pharmaceutical field representatives.

The business problem here is that after meeting a healthcare professional, a field rep usually has to translate an unstructured memory of the interaction into a structured CRM entry. That process is repetitive, easy to get wrong, and often slows down field documentation.

So the core idea of this product is to let the rep describe the interaction naturally in chat, while the AI assistant translates that into structured CRM data.

This assignment had one especially important rule: the form should not be manually filled in the usual way. Instead, the AI assistant should control the form. I designed the product around that rule, so the form is AI-driven and the assistant becomes the primary input surface."

### What to show on screen

- Open the app
- Keep both panels visible
- Point out:
  - left side = structured interaction form
  - right side = AI assistant chat

### Strong transition line

"So before I go into the technical implementation, I want to quickly show the product experience and explain why the UI is structured this way."

---

## 2. Product Overview and UX Decisions - 5 minutes

### What to say

"The application uses a split-screen layout because the user needs two things visible at the same time:

1. the structured CRM record being built
2. the conversational interface controlling it

The left panel is the structured source of truth. It contains the form fields for the HCP interaction.

The right panel is the AI assistant. The user talks to the assistant in natural language, and the assistant updates the form through LangGraph tools.

This creates a strong separation of roles:

- the chat is the control layer
- the form is the structured output layer

That separation is important for trust and usability, because the user can always see exactly how their natural-language request translated into structured CRM data."

### Highlight these specific UX choices

Say:

"I also added a few product behaviors to improve clarity and reduce error:

- changed fields are highlighted so the user sees exactly what the AI updated
- missing required fields are flagged so partial logs are still useful
- date values are normalized automatically
- the assistant uses multi-turn context, so it can continue refining the same interaction over multiple messages
- follow-up suggestions include a priority and next follow-up date
- typo correction helps avoid saving the wrong HCP name
- previous saved interaction flows can be loaded back into the form"

### What to show

- Point to stored interactions area
- Point to `Form Name`
- Point to `Unique ID`
- Point to follow-up section
- Point to chat history

### Strong transition line

"With that product framing in place, I’ll move into the live demo, starting with the most important workflow: logging a new interaction through AI."

---

## 3. Live Demo - Primary Workflow - 10 minutes

This is the most important part of the recording.

### Step 1: Start with a clean state

Click `Reset`.

Say:

"I’m starting from a clean interaction state. The form is empty except for defaults like date and time."

---

### Step 2: Log a new interaction with natural language

Paste this:

`Today I met Dr. Priya Mehta and discussed Product X efficacy. The sentiment was positive, I shared brochures, and we agreed to review trial data next week.`

### What to say while waiting

"Here the user is not selecting fields one by one. Instead, they are describing the meeting naturally.

The assistant extracts the structured details from the message and maps them into the form."

### What to point out after response

- HCP name
- date
- topics discussed
- sentiment
- materials shared
- follow-up-related data if present

Say:

"The form is now auto-populated from the assistant response. This is the main assignment requirement in action: AI-driven form control instead of manual form entry."

### Mention highlight behavior

"The changed fields are visually highlighted so the user knows exactly what the assistant just updated."

---

### Step 3: Show form identity

Say:

"I also added a form identity layer. Each saved interaction has:

- a human-readable form name
- a unique interaction ID

The form name can be changed manually for labeling purposes, and it can also be updated through chat."

You can type in `Form Name` manually or save this for later.

---

### Step 4: Show targeted edit behavior

Paste:

`Change only the sentiment to Negative and change the time to 15:30`

Say:

"This demonstrates the edit tool. The important behavior here is precision: the assistant updates only the fields explicitly mentioned, and the rest of the form remains intact."

Show:

- sentiment changed
- time changed
- all other fields preserved

This is important to say:

"That selective update behavior is one of the assignment’s mandatory requirements."

---

### Step 5: Save the interaction

Click `Save`.

Say:

"Now I’m saving the interaction to the backend. On save, the app stores the structured interaction record and assigns a unique interaction ID if one doesn’t already exist."

Show:

- success state
- stored interactions section
- `interaction_uid`

### Strong transition line

"So that covers the main workflow. Next I’ll show a few higher-value behaviors that make the assistant more practical in real CRM usage."

---

## 4. Live Demo - Advanced Scenarios - 8 minutes

### Scenario A: Missing field detection

Reset the form or begin a new partial prompt:

`Met Dr. Rajesh Kumar and discussed oncology updates`

Say:

"This is intentionally incomplete. In a real field scenario, reps often capture only part of the interaction at first. The system should still help rather than fail."

Show:

- partial form update
- missing fields banner
- assistant message listing missing values

Say:

"This is missing field detection. The assistant extracts what it can, keeps momentum, and explicitly surfaces what still needs to be captured."

---

### Scenario B: Multi-turn memory

Now add:

`The sentiment was positive and I shared a product brochure`

Say:

"This is a multi-turn continuation. The assistant receives the current form state along with the new message, so it can incrementally refine the same interaction rather than starting over each time."

Show:

- missing fields reduced
- additional fields populated

---

### Scenario C: Typo correction / error correction

Paste:

`Met Dr. Sharm and discussed treatment adoption`

Say:

"This demonstrates the error-correction system. If the user types a likely HCP typo, the assistant proposes a likely correction instead of silently saving a wrong name."

Show:

- `Did you mean ... ?`

Say:

"This matters in CRM systems because wrong entity identity is usually much more expensive than a missing field."

---

### Scenario D: Follow-up intelligence

Paste:

`Suggest follow-up actions for this interaction`

Then:

`Add follow-up action: schedule a visit next Friday`

Say:

"This shows the follow-up workflow. The assistant can generate structured next steps, estimate priority, and suggest the next follow-up date based on the interaction context."

Show:

- AI suggested follow-ups
- priority
- next follow-up date
- follow-up actions field

Say:

"This moves the product beyond passive logging and into action-oriented CRM support."

---

### Scenario E: Search tool

Paste:

`Search for Dr. Priya Mehta`

Say:

"This demonstrates the HCP search tool. It can retrieve a matching HCP profile and return supporting identity context such as specialty and hospital."

Show:

- matching result in chat

### Scenario F: Load saved interactions

Click `Refresh` in stored interactions and load one.

Say:

"I also added stored interaction retrieval, so previous records can be loaded back into the form. This is important because the assignment is not only about AI-assisted entry, but also about persistence and review."

Show:

- stored list
- loaded form
- form name
- unique ID

### Strong transition line

"Now that I’ve shown the product behavior, I’ll explain how it is implemented under the hood, starting with LangGraph."

---

## 5. LangGraph Architecture Deep Dive - 6 minutes

Open:

- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py)

### What to say

"The assignment explicitly requires LangGraph and an LLM, and specifically warns against hard-coded logic replacing those technologies. So I implemented the assistant around a LangGraph tool architecture.

At a high level, the agent has:

- a state structure for messages and current form state
- a tool layer
- a routing step that determines which tool should handle the user request
- an execution flow that merges tool results back into the CRM form state"

### Explain the tool model

Say:

"The five tools are:

1. `log_interaction`
2. `edit_interaction`
3. `suggest_followup`
4. `search_hcp`
5. `analyze_sentiment`

These tools are exposed as LangGraph-compatible tools and bound to the LLM."

### Explain each tool in a senior way

#### `log_interaction`

"This tool converts natural language into structured CRM fields. It extracts entities and field values like HCP name, date, topics discussed, materials shared, and sentiment. It is the main entry point for new interaction logging."

#### `edit_interaction`

"This tool is intentionally narrow. It extracts only explicitly requested changes, so the assistant can update one or two fields without overwriting the rest of the record."

#### `suggest_followup`

"This tool uses the interaction context to generate actionable next steps, a priority level, and a proposed next follow-up date."

#### `search_hcp`

"This tool resolves HCP search requests and supports typo-aware matching."

#### `analyze_sentiment`

"This tool focuses only on inferred sentiment classification when the user asks for analysis rather than a direct edit."

### Explain orchestration

Say:

"The backend also sends the current form state into the agent. That gives the assistant multi-turn awareness. So when the user says something like 'change only the sentiment' or 'suggest a follow-up,' the assistant is operating on the current interaction rather than on an isolated message."

### Explain why this is not just hard-coded

Say:

"There is lightweight deterministic routing in front to keep the experience stable, but the core field extraction and tool behaviors are still LLM-driven and implemented through the LangGraph tool structure, which keeps it aligned with the assignment requirement."

### Strong transition line

"Next I’ll show how those tool outputs move through the backend and into persistence."

---

## 6. Backend, Database, and Persistence - 4 minutes

Open:

- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\main.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\main.py)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\database.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\database.py)

### What to say

"The backend is implemented with FastAPI. It exposes:

- `/api/chat` for AI interaction
- `/api/interactions` for save and list
- `/api/interactions/{id}` for loading a specific interaction
- `/api/hcps/search` for HCP search
- `/health` for service health"

### Explain flow

"When the frontend sends a chat request, it includes:

- the chat history
- the current form state

The backend runs the agent, gets the tool result, and returns structured data back to the frontend.

The frontend then maps those fields directly into Redux state, which updates the left-side form."

### Explain persistence

"For persistence, the interaction model stores:

- form identity
- HCP information
- interaction details
- discussion summary
- shared materials
- sentiment
- follow-up actions
- follow-up priority
- next follow-up date
- AI suggestions

I also added `form_name` and `interaction_uid` so each saved log is easier to identify and reload."

### Explain DB fallback honestly

"The project is designed for PostgreSQL, but I also added a SQLite fallback so the demo remains usable if local Postgres credentials are unavailable or misconfigured. That gives the evaluator a reliable working demo while preserving the main persistence workflow."

### Strong transition line

"Finally, I’ll close with a short summary of what this implementation satisfies and what I intentionally added beyond the minimum requirement."

---

## 7. Wrap-Up and Submission Summary - 3 minutes

### What to say

"To summarize, this implementation satisfies the core assignment requirements:

1. split-screen layout
2. left-side form and right-side AI assistant
3. AI-driven form control rather than manual entry
4. LangGraph-based implementation
5. at least five tools
6. mandatory logging and edit workflows

In addition, I added:

- field highlight feedback
- missing field detection
- auto date normalization
- multi-turn context support
- follow-up priority and next date suggestions
- typo correction for HCP names
- stored interaction retrieval
- form naming and unique interaction IDs

So the product is not only compliant with the assignment, but also closer to something that feels practical and usable in a real CRM setting."

### Final line

"Thank you. I’d be happy to walk through any part of the architecture or code in more detail."

---

## Optional Q&A Prep

### If asked: "Why LangGraph?"

Say:

"LangGraph is a strong fit because this is a multi-step, tool-driven conversational workflow. It gives a clean way to represent agent state, bind tools, and manage transitions between reasoning and action. That makes the architecture more extensible than a single prompt-response pipeline."

### If asked: "Why Redux?"

Say:

"Redux keeps the form state predictable. Since the assistant, stored-record loading, save flow, and UI highlighting all modify shared interaction state, Redux makes those updates easier to reason about and debug."

### If asked: "How do you prevent overwriting fields?"

Say:

"The edit tool is intentionally scoped to only return explicitly requested fields, and the frontend merges only the returned values instead of resetting the whole form."

### If asked: "What happens if the model makes a mistake?"

Say:

"There are a few safeguards: field highlighting makes changes visible, typo correction reduces identity mistakes, missing field detection keeps incomplete logs explicit, and targeted edit lets the user correct only the exact field they want."

### If asked: "Why the SQLite fallback?"

Say:

"For demo reliability. It preserves the persistence flow even if local PostgreSQL credentials or local service configuration become a blocker."

---

## Recommended Prompt Sequence For A Stable 40-Minute Demo

Use these in order:

1. `Today I met Dr. Priya Mehta and discussed Product X efficacy. The sentiment was positive, I shared brochures, and we agreed to review trial data next week.`
2. `Change only the sentiment to Negative and change the time to 15:30`
3. `Met Dr. Rajesh Kumar and discussed oncology updates`
4. `The sentiment was positive and I shared a product brochure`
5. `Met Dr. Sharm and discussed treatment adoption`
6. `Suggest follow-up actions for this interaction`
7. `Add follow-up action: schedule a visit next Friday`
8. `Search for Dr. Priya Mehta`
9. `Rename this form to Cardiology product efficacy follow-up`

---

## Presenter Notes

- Speak slower than you think you need to
- Pause when the form updates so the evaluator can see the behavior
- Keep code references short and purposeful
- When showing code, explain intent first, then point at the file
- In the live demo, narrate outcomes, not just clicks

---

## Suggested Files To Keep Ready During The Demo

- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\README.md](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\README.md)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\main.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\main.py)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\database.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\database.py)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\ChatPanel.jsx](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\ChatPanel.jsx)
- [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\InteractionForm.jsx](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\frontend\src\components\InteractionForm.jsx)
