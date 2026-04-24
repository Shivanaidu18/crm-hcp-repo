# 10-15 Minute Evaluator Demo Script

This script is written so you can follow it naturally during a screen recording. You do not need to read every line word-for-word, but if you stay close to this flow you will cover the assignment clearly.

## 1. Opening - 1 minute

Say:

"Hi, this is my AI-first CRM HCP interaction logging module. The app uses a split-screen layout. On the left is the interaction form, and on the right is the AI assistant. The key requirement for this assignment is that the form is AI-driven. Users do not manually fill the main form fields. Instead, they interact with the assistant in natural language, and the assistant updates the form through LangGraph tools."

While saying this:

- Show the left form
- Show the right chat panel
- Point out that the left side is the structured interaction form
- Point out that the right side is the assistant used to populate and edit the form

## 2. Architecture Summary - 1 to 2 minutes

Say:

"The frontend is built with React and Redux. The backend is FastAPI. The assistant is implemented using LangGraph and Groq. I used five tools in the LangGraph workflow:

1. log_interaction
2. edit_interaction
3. suggest_followup
4. search_hcp
5. analyze_sentiment

The Redux store keeps the form state, and the assistant sends structured tool results back to the UI so the form updates automatically."

Optional visual:

- Open [C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py](C:\Users\sivan\Downloads\crm-hcp-project\crm-hcp\backend\agent.py)
- Briefly point at the tool definitions

## 3. Show That Manual Entry Is Restricted - 1 minute

Say:

"A major evaluation rule is that the form should not be manually filled in the normal workflow. The main interaction fields are AI-controlled. The user speaks to the assistant, and the assistant populates the form."

While saying this:

- Click into a read-only field like HCP Name or Topics Discussed
- Show that it is AI-populated / controlled
- Mention that `form_name` is intentionally editable so the saved interaction can be labeled clearly, and it can also be updated by AI

## 4. Primary Demo: Log a New Interaction - 2 minutes

Paste this in the chat:

`Today I met Dr. Priya Mehta and discussed Product X efficacy. The sentiment was positive, I shared brochures, and we agreed to review trial data next week.`

Say:

"Now I’m logging a new HCP interaction entirely through chat. The assistant extracts the HCP name, date, discussion summary, sentiment, materials shared, and follow-up context, then updates the form."

Pause and show:

- HCP name updated
- Date normalized
- Topics discussed updated
- Sentiment updated
- Materials shared updated
- Follow-up section updated if generated
- Changed field highlight glow

Call out:

"The yellow highlight shows exactly which fields changed."

## 5. Targeted Edit Demo - 1.5 minutes

Paste this:

`Change only the sentiment to Negative and change the time to 15:30`

Say:

"This demonstrates the edit tool. The assistant changes only the requested fields and leaves the rest of the form intact."

Show:

- sentiment changed
- time changed
- other fields unchanged

## 6. Missing Field Detection - 1 minute

Reset the form or use a short incomplete prompt:

`Met Dr. Rajesh Kumar and discussed oncology updates`

Say:

"This also supports missing field detection. If the interaction is incomplete, the assistant still populates what it can and flags the remaining required fields."

Show:

- missing fields banner
- assistant message listing what is still missing

## 7. Typo Correction / Error Correction - 1 minute

Paste:

`Met Dr. Sharm and discussed treatment adoption`

Say:

"This is the error-correction behavior. If the user types a likely HCP typo, the assistant proposes the closest known match instead of silently saving the wrong name."

Show:

- assistant response like "Did you mean Dr. Arjun Sharma?" or similar

## 8. Multi-Turn Memory and Follow-Up Suggestions - 1.5 to 2 minutes

After a partially filled form, paste:

`Suggest follow-up actions for this interaction`

Then paste:

`Add follow-up action: schedule a visit next Friday`

Say:

"The assistant receives the current form state with each message, so it can work across multiple turns. It can suggest follow-up actions, assign a priority, and recommend the next follow-up date using the already captured interaction context."

Show:

- AI suggested follow-ups list
- priority
- next follow-up date

## 9. Search Tool Demo - 1 minute

Paste:

`Search for Dr. Priya Mehta`

Say:

"This is the HCP search tool. It can search known HCP data and return matching records. In a production version this would connect to a live directory, but the tool flow is already in place."

Show:

- matching HCP result in chat

## 10. Save and Retrieve Previous Logs - 1.5 minutes

Click `Save`.

Say:

"Each interaction can be saved and assigned a unique interaction ID plus a human-readable form name."

Show:

- `form_name`
- `interaction_uid`

Then:

- Open the Stored Interactions section
- Click `Refresh`
- Load a previous stored item

Say:

"This section shows previous interaction flows stored in the backend database, and they can be loaded back into the form for review."

## 11. Closing Summary - 1 minute

Say:

"To summarize, this implementation meets the core assignment requirements:

1. split-screen layout
2. AI assistant controls form population
3. LangGraph-based tool workflow
4. at least five tools implemented
5. targeted edit behavior
6. stored interaction retrieval

In addition, I added field highlighting, missing field detection, date normalization, typo correction, multi-turn context, follow-up scheduling metadata, and saved interaction viewing."

## Recommended Recording Tips

- Keep browser zoom around 100 percent so both panels stay visible
- Use 3 to 4 prepared prompts instead of too many improvised ones
- If one LLM response is slow, briefly narrate what it is doing instead of waiting silently
- Keep the code walkthrough short; focus most of the video on the working product

## Suggested Prompt Set For Recording

Use this exact sequence if you want a stable recording:

1. `Today I met Dr. Priya Mehta and discussed Product X efficacy. The sentiment was positive, I shared brochures, and we agreed to review trial data next week.`
2. `Change only the sentiment to Negative and change the time to 15:30`
3. `Met Dr. Rajesh Kumar and discussed oncology updates`
4. `Met Dr. Sharm and discussed treatment adoption`
5. `Suggest follow-up actions for this interaction`
6. `Search for Dr. Priya Mehta`
7. `Rename this form to Cardiology product efficacy follow-up`

## Backup Line If Asked About Database Behavior

If the evaluator asks about persistence, say:

"The app supports PostgreSQL and also includes a SQLite fallback so the demo remains usable even if local Postgres credentials are not configured correctly."
