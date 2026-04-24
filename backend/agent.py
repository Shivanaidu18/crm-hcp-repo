"""
LangGraph AI Agent for the HCP CRM module.
"""
import ast
import json
import os
import re
from datetime import datetime, timedelta
from difflib import get_close_matches
from typing import Annotated, Any, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
KNOWN_HCPS = [
    {"id": 1, "name": "Dr. Arjun Sharma", "specialty": "Oncology", "hospital": "Apollo Hospitals", "email": "arjun.sharma@apollo.com"},
    {"id": 2, "name": "Dr. Priya Mehta", "specialty": "Cardiology", "hospital": "AIIMS Delhi", "email": "priya.mehta@aiims.edu"},
    {"id": 3, "name": "Dr. Rajesh Kumar", "specialty": "Neurology", "hospital": "Fortis Healthcare", "email": "r.kumar@fortis.in"},
    {"id": 4, "name": "Dr. Anita Desai", "specialty": "Endocrinology", "hospital": "Narayana Health", "email": "a.desai@narayana.com"},
    {"id": 5, "name": "Dr. Smith", "specialty": "General Medicine", "hospital": "City Medical Center", "email": "smith@citymed.com"},
]
REQUIRED_FIELDS = ["hcp_name", "interaction_type", "date", "topics_discussed", "sentiment"]


def make_llm(temperature: float = 0.2) -> ChatGroq:
    return ChatGroq(
        model=MODEL_NAME,
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=temperature,
    )


def parse_json_object(text: str) -> dict:
    raw = text.strip()
    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
    return json.loads(raw)


def normalize_date_value(value: str | None) -> str | None:
    if not value:
        return None

    normalized = value.strip().lower()
    today = datetime.now().date()
    if normalized == "today":
        return today.isoformat()
    if normalized == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    if normalized == "yesterday":
        return (today - timedelta(days=1)).isoformat()

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date().isoformat()
        except ValueError:
            continue

    return value


def normalize_time_value(value: str | None) -> str | None:
    if not value:
        return None
    for fmt in ("%H:%M", "%I:%M %p", "%I %p"):
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%H:%M")
        except ValueError:
            continue
    return value


def find_hcp_correction(name: str | None) -> dict | None:
    if not name:
        return None
    exact = next((hcp for hcp in KNOWN_HCPS if hcp["name"].lower() == name.lower()), None)
    if exact:
        return exact
    names = [hcp["name"] for hcp in KNOWN_HCPS]
    match = get_close_matches(name, names, n=1, cutoff=0.72)
    if not match:
        return None
    return next((hcp for hcp in KNOWN_HCPS if hcp["name"] == match[0]), None)


def merge_form_state(current_form: dict[str, Any] | None, fields: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(current_form or {})
    for key, value in (fields or {}).items():
      if value not in (None, "", []):
        merged[key] = value
    return merged


def build_form_name(form_state: dict[str, Any]) -> str:
    if form_state.get("form_name"):
        return form_state["form_name"]
    hcp = form_state.get("hcp_name") or "Untitled Interaction"
    interaction_type = form_state.get("interaction_type") or "Meeting"
    return f"{hcp} - {interaction_type}"


def detect_missing_fields(form_state: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if not form_state.get(field)]


def fallback_followup_date(form_state: dict[str, Any], priority: str | None) -> str:
    base = normalize_date_value(form_state.get("date")) or datetime.now().date().isoformat()
    base_date = datetime.strptime(base, "%Y-%m-%d").date()
    days = 7
    if (priority or "").lower() == "high":
        days = 3
    elif (priority or "").lower() == "low":
        days = 14
    return (base_date + timedelta(days=days)).isoformat()


def classify_request(user_text: str) -> str:
    text = user_text.lower()
    if any(token in text for token in ["search", "find", "look up", "lookup", "show profile", "who is"]):
        return "search_hcp"
    if any(token in text for token in ["change", "update", "edit", "correct", "fix", "replace", "add follow-up action"]):
        return "edit_interaction"
    if "suggest" in text or "follow-up" in text or "follow up" in text or "next visit" in text:
        return "suggest_followup"
    if "sentiment" in text and any(token in text for token in ["analyze", "assess", "infer", "what is", "overall"]):
        return "analyze_sentiment"
    return "log_interaction"


def route_tool_call(user_text: str, current_form: dict[str, Any]) -> list[dict]:
    route = classify_request(user_text)
    results = []

    if route == "search_hcp":
        query = re.sub(r"(?i)\b(search|find|look up|lookup|show profile for|show profile of|show profile)\b", "", user_text).strip(" :")
        results.append(search_hcp.invoke({"query": query or user_text}))
        return results

    if route == "edit_interaction":
        results.append(edit_interaction.invoke({"edit_instruction": user_text}))
        return results

    if route == "analyze_sentiment":
        context = user_text
        if current_form.get("topics_discussed"):
            context = json.dumps(current_form, ensure_ascii=True)
        results.append(analyze_sentiment.invoke({"text": context}))
        return results

    if route == "suggest_followup":
        results.append(suggest_followup.invoke({"interaction_context": json.dumps(current_form, ensure_ascii=True)}))
        return results

    log_result = log_interaction.invoke({"user_message": user_text})
    results.append(log_result)

    merged_state = merge_form_state(current_form, log_result.get("fields", {}))
    if not log_result.get("suggested_hcp") and merged_state.get("hcp_name") and merged_state.get("topics_discussed"):
        results.append(suggest_followup.invoke({"interaction_context": json.dumps(merged_state, ensure_ascii=True)}))

    return results


@tool
def log_interaction(user_message: str) -> dict:
    """Extract structured CRM interaction fields from a natural-language note."""
    system_prompt = f"""You extract structured data for a pharmaceutical CRM.
Return only valid JSON. Use null for missing values.

Schema:
{{
  "form_name": "string or null",
  "hcp_name": "string or null",
  "interaction_type": "Meeting|Call|Email|Conference|Visit or null",
  "date": "YYYY-MM-DD or relative token like today if needed",
  "time": "HH:MM or null",
  "attendees": "comma-separated names or null",
  "topics_discussed": "string summary or null",
  "materials_shared": "comma-separated materials or null",
  "samples_distributed": "comma-separated samples or null",
  "sentiment": "Positive|Neutral|Negative or null",
  "outcomes": "string or null",
  "follow_up_actions": "string or null"
}}

Today's date is {datetime.now().strftime("%Y-%m-%d")}.
"""
    try:
        response = make_llm(temperature=0).invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])
        fields = parse_json_object(response.content)
        fields["date"] = normalize_date_value(fields.get("date"))
        fields["time"] = normalize_time_value(fields.get("time"))
        fields["form_name"] = fields.get("form_name") or build_form_name(fields)

        correction = find_hcp_correction(fields.get("hcp_name"))
        if fields.get("hcp_name") and correction and correction["name"].lower() != fields["hcp_name"].lower():
            fields.pop("hcp_name", None)
            return {
                "action": "log_interaction",
                "fields": fields,
                "missing_fields": ["hcp_name"],
                "message": f"Did you mean {correction['name']}? I updated the rest of the interaction but held the HCP name until you confirm.",
                "suggested_hcp": correction["name"],
            }

        return {
            "action": "log_interaction",
            "fields": fields,
            "message": "Interaction logged successfully. The form fields were populated from your summary. I can also suggest follow-up actions.",
        }
    except Exception as exc:
        return {
            "action": "log_interaction",
            "fields": {},
            "message": f"I could not parse the interaction details. Please rephrase and try again. Error: {exc}",
        }


@tool
def edit_interaction(edit_instruction: str) -> dict:
    """Extract only the explicitly requested CRM field updates from an edit request."""
    system_prompt = """You edit a CRM form.
Extract only the fields explicitly requested by the user. Omit unchanged fields.
Return only valid JSON.

Allowed fields:
form_name, hcp_name, interaction_type, date, time, attendees, topics_discussed,
materials_shared, samples_distributed, sentiment, outcomes, follow_up_actions
"""
    try:
        response = make_llm(temperature=0).invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=edit_instruction),
        ])
        fields = parse_json_object(response.content)
        fields["date"] = normalize_date_value(fields.get("date"))
        fields["time"] = normalize_time_value(fields.get("time"))
        field_list = ", ".join(fields.keys()) or "none"
        return {
            "action": "edit_interaction",
            "fields": fields,
            "message": f"Updated successfully. Changed field(s): {field_list}. All other data remains intact.",
        }
    except Exception as exc:
        return {
            "action": "edit_interaction",
            "fields": {},
            "message": f"I could not parse the edit instruction. Please try again. Error: {exc}",
        }


@tool
def suggest_followup(interaction_context: str) -> dict:
    """Generate follow-up suggestions, a priority level, and the next follow-up date."""
    system_prompt = f"""You are a pharmaceutical sales coach.
Return only valid JSON:
{{
  "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "priority": "High|Medium|Low",
  "next_follow_up_date": "YYYY-MM-DD",
  "next_meeting_recommendation": "string"
}}

Today is {datetime.now().strftime("%Y-%m-%d")}.
Suggestions must be specific, compliant, and actionable.
"""
    try:
        response = make_llm(temperature=0.5).invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=interaction_context),
        ])
        result = parse_json_object(response.content)
        suggestions = result.get("suggestions", [])
        formatted = "\n".join([f"- {item}" for item in suggestions])
        return {
            "action": "suggest_followup",
            "suggestions": suggestions,
            "priority": result.get("priority", "Medium"),
            "next_follow_up_date": normalize_date_value(result.get("next_follow_up_date")),
            "next_meeting": result.get("next_meeting_recommendation", ""),
            "message": f"AI suggested follow-ups:\n{formatted}",
        }
    except Exception as exc:
        return {
            "action": "suggest_followup",
            "suggestions": [],
            "message": f"Could not generate follow-up suggestions. Error: {exc}",
        }


@tool
def search_hcp(query: str) -> dict:
    """Search known HCP records by name, specialty, or hospital."""
    q = query.lower()
    results = [
        hcp for hcp in KNOWN_HCPS
        if q in hcp["name"].lower() or q in hcp["specialty"].lower() or q in hcp["hospital"].lower()
    ]

    if not results:
        fuzzy = find_hcp_correction(query)
        if fuzzy:
            return {
                "action": "search_hcp",
                "results": [fuzzy],
                "message": f"Did you mean {fuzzy['name']}? I found this likely HCP match.",
            }
        results = KNOWN_HCPS[:3]

    lines = "\n".join([f"- {hcp['name']} - {hcp['specialty']} @ {hcp['hospital']}" for hcp in results])
    return {
        "action": "search_hcp",
        "results": results,
        "message": f"Found {len(results)} HCP(s) matching '{query}':\n{lines}",
    }


@tool
def analyze_sentiment(text: str) -> dict:
    """Infer Positive, Neutral, or Negative sentiment for an interaction summary."""
    system_prompt = """You classify pharmaceutical sales interaction sentiment.
Return only valid JSON:
{
  "sentiment": "Positive|Neutral|Negative",
  "confidence": 0.0,
  "reasoning": "brief explanation"
}
"""
    try:
        response = make_llm(temperature=0).invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=text),
        ])
        result = parse_json_object(response.content)
        sentiment = result.get("sentiment", "Neutral")
        return {
            "action": "analyze_sentiment",
            "sentiment": sentiment,
            "confidence": result.get("confidence", 0.5),
            "reasoning": result.get("reasoning", ""),
            "fields": {"sentiment": sentiment},
            "message": f"Sentiment analysis: {sentiment} (confidence: {int(result.get('confidence', 0.5) * 100)}%)\n{result.get('reasoning', '')}",
        }
    except Exception as exc:
        return {
            "action": "analyze_sentiment",
            "sentiment": "Neutral",
            "fields": {"sentiment": "Neutral"},
            "message": f"Could not analyze sentiment. Error: {exc}",
        }


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_form: dict[str, Any]


tools = [log_interaction, edit_interaction, suggest_followup, search_hcp, analyze_sentiment]
llm_with_tools = make_llm().bind_tools(tools)


def agent_node(state: AgentState):
    current_form = json.dumps(state.get("current_form", {}), ensure_ascii=True)
    system_message = SystemMessage(content=f"""You are an AI assistant for a pharmaceutical CRM HCP interaction form.

Current form state:
{current_form}

Tool routing:
- New meeting/call/email/visit description: log_interaction
- Corrections or field changes: edit_interaction
- Follow-up suggestions or scheduling: suggest_followup
- HCP lookup: search_hcp
- Sentiment-only analysis: analyze_sentiment

Important:
- The user cannot edit the form manually; your tool results drive form updates.
- If the user says change, update, edit, correct, or fix, use edit_interaction.
- Use analyze_sentiment only when the user asks to infer or assess sentiment, not when they ask to change it.
- If the user describes an interaction with clues like met, discussed, shared, sentiment, samples, outcomes, date, or follow-up, use log_interaction even if an HCP name appears.
- Use search_hcp only when the user explicitly asks to search, find, look up, or retrieve an HCP profile.
- Be concise and professional.
""")
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")
agent_graph = graph.compile()


def parse_tool_content(content: str) -> dict | None:
    try:
        return json.loads(content)
    except Exception:
        try:
            value = ast.literal_eval(content)
            return value if isinstance(value, dict) else {"raw": content}
        except Exception:
            return {"raw": content}


def run_agent(messages: list[dict], current_form: dict[str, Any] | None = None) -> dict:
    current_form = current_form or {}
    latest_user = next((message["content"] for message in reversed(messages) if message["role"] == "user"), "")
    if latest_user:
        tool_results = route_tool_call(latest_user, current_form)
        ai_response = tool_results[-1].get("message", "I processed your request.") if tool_results else "I processed your request."
    else:
        tool_results = []
        ai_response = ""

    if not tool_results:
        lc_messages = []
        for message in messages:
            if message["role"] == "user":
                lc_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                lc_messages.append(AIMessage(content=message["content"]))

        result = agent_graph.invoke({"messages": lc_messages, "current_form": current_form})
        final_messages = result["messages"]

        for message in reversed(final_messages):
            if isinstance(message, AIMessage) and message.content and not ai_response:
                ai_response = message.content

        for message in final_messages:
            if isinstance(message, ToolMessage):
                parsed = parse_tool_content(message.content)
                if parsed:
                    tool_results.append(parsed)

    tool_result = None
    if tool_results:
        combined_fields = {}
        combined_suggestions = []
        combined_results = []
        preferred_message = None
        preferred_action = None
        combined_priority = None
        combined_next_date = None

        for item in tool_results:
            fields = item.get("fields")
            if isinstance(fields, dict):
                combined_fields.update({key: value for key, value in fields.items() if value is not None})

            if isinstance(item.get("suggestions"), list):
                combined_suggestions = item["suggestions"]

            if isinstance(item.get("results"), list):
                combined_results = item["results"]

            if item.get("priority"):
                combined_priority = item["priority"]

            if item.get("next_follow_up_date"):
                combined_next_date = item["next_follow_up_date"]

            action = item.get("action")
            if action in {"log_interaction", "edit_interaction", "analyze_sentiment", "suggest_followup"}:
                preferred_action = action
                preferred_message = item.get("message", preferred_message)
            elif preferred_message is None:
                preferred_action = action
                preferred_message = item.get("message")

        merged_state = merge_form_state(current_form, combined_fields)
        missing_fields = detect_missing_fields(merged_state)
        if combined_suggestions and not combined_next_date:
            combined_next_date = fallback_followup_date(merged_state, combined_priority)

        tool_result = {
            "action": preferred_action or tool_results[-1].get("action"),
            "message": preferred_message or tool_results[-1].get("message") or ai_response,
            "missing_fields": missing_fields,
        }
        if combined_fields:
            tool_result["fields"] = combined_fields
        if combined_suggestions:
            tool_result["suggestions"] = combined_suggestions
        if combined_results:
            tool_result["results"] = combined_results
        if combined_priority:
            tool_result["priority"] = combined_priority
        if combined_next_date:
            tool_result["next_follow_up_date"] = combined_next_date

        if missing_fields and tool_result["action"] in {"log_interaction", "edit_interaction"}:
            tool_result["message"] = f"{tool_result['message']}\nStill missing: {', '.join(missing_fields)}."

    return {
        "response": ai_response or "I processed your request.",
        "tool_result": tool_result,
    }
