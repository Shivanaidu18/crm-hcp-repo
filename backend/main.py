"""
FastAPI Backend for AI-First CRM HCP Module
"""
import os
import uuid
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_agent
from database import ACTIVE_DATABASE_URL, HCP, Interaction, SessionLocal, create_tables

load_dotenv()

app = FastAPI(title="CRM HCP AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    try:
        create_tables()
        print(f"Database tables created using {ACTIVE_DATABASE_URL}")
    except Exception as exc:
        print(f"DB init skipped (no DB connected): {exc}")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    current_form: Optional[Dict[str, Any]] = None


class InteractionCreate(BaseModel):
    form_name: Optional[str] = None
    hcp_name: Optional[str] = None
    hcp_id: Optional[int] = None
    interaction_type: Optional[str] = "Meeting"
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = "Neutral"
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    follow_up_priority: Optional[str] = None
    next_follow_up_date: Optional[str] = None
    ai_suggested_followups: Optional[List[str]] = []
    raw_chat_log: Optional[str] = None


class InteractionUpdate(BaseModel):
    form_name: Optional[str] = None
    hcp_name: Optional[str] = None
    hcp_id: Optional[int] = None
    interaction_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    follow_up_priority: Optional[str] = None
    next_follow_up_date: Optional[str] = None
    ai_suggested_followups: Optional[List[str]] = None


def serialize_interaction(interaction: Interaction) -> Dict[str, Any]:
    return {
        "id": interaction.id,
        "interaction_uid": interaction.interaction_uid,
        "form_name": interaction.form_name,
        "hcp_name": interaction.hcp_name,
        "hcp_id": interaction.hcp_id,
        "interaction_type": interaction.interaction_type,
        "date": interaction.date,
        "time": interaction.time,
        "attendees": interaction.attendees,
        "topics_discussed": interaction.topics_discussed,
        "materials_shared": interaction.materials_shared,
        "samples_distributed": interaction.samples_distributed,
        "sentiment": interaction.sentiment,
        "outcomes": interaction.outcomes,
        "follow_up_actions": interaction.follow_up_actions,
        "follow_up_priority": interaction.follow_up_priority,
        "next_follow_up_date": interaction.next_follow_up_date,
        "ai_suggested_followups": interaction.ai_suggested_followups or [],
        "raw_chat_log": interaction.raw_chat_log,
        "created_at": str(interaction.created_at) if interaction.created_at else None,
        "updated_at": str(interaction.updated_at) if interaction.updated_at else None,
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        result = run_agent(messages, request.current_form or {})
        return {
            "response": result["response"],
            "tool_result": result.get("tool_result"),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/interactions")
def create_interaction(data: InteractionCreate):
    db = SessionLocal()
    try:
        payload = data.dict()
        payload["interaction_uid"] = payload.get("interaction_uid") if "interaction_uid" in payload else None
        if not payload["interaction_uid"]:
            payload["interaction_uid"] = f"INT-{uuid.uuid4().hex[:8].upper()}"
        if not payload.get("form_name"):
            base_name = payload.get("hcp_name") or "Untitled Interaction"
            payload["form_name"] = f"{base_name} Log"
        interaction = Interaction(**payload)
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return {
            "id": interaction.id,
            "interaction_uid": interaction.interaction_uid,
            "form_name": interaction.form_name,
            "message": "Interaction saved successfully",
        }
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        db.close()


@app.get("/api/interactions")
def list_interactions():
    db = SessionLocal()
    try:
        interactions = (
            db.query(Interaction)
            .order_by(Interaction.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "id": item.id,
                "interaction_uid": item.interaction_uid,
                "form_name": item.form_name,
                "hcp_name": item.hcp_name,
                "interaction_type": item.interaction_type,
                "date": item.date,
                "sentiment": item.sentiment,
                "topics_discussed": item.topics_discussed,
                "follow_up_priority": item.follow_up_priority,
                "next_follow_up_date": item.next_follow_up_date,
                "created_at": str(item.created_at) if item.created_at else None,
            }
            for item in interactions
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load interactions: {exc}")
    finally:
        db.close()


@app.get("/api/interactions/{interaction_id}")
def get_interaction(interaction_id: int):
    db = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            raise HTTPException(status_code=404, detail="Not found")
        return serialize_interaction(interaction)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load interaction {interaction_id}: {exc}")
    finally:
        db.close()


@app.put("/api/interactions/{interaction_id}")
def update_interaction(interaction_id: int, data: InteractionUpdate):
    db = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            raise HTTPException(status_code=404, detail="Not found")

        update_data = {key: value for key, value in data.dict().items() if value is not None}
        for key, value in update_data.items():
            setattr(interaction, key, value)
        db.commit()
        return {"message": "Updated successfully"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        db.close()


@app.get("/api/hcps/search")
def search_hcps(q: str = ""):
    db = SessionLocal()
    try:
        query = db.query(HCP)
        if q:
            query = query.filter(
                HCP.name.ilike(f"%{q}%") |
                HCP.specialty.ilike(f"%{q}%") |
                HCP.hospital.ilike(f"%{q}%")
            )
        hcps = query.limit(10).all()
        if hcps:
            return [
                {"id": item.id, "name": item.name, "specialty": item.specialty, "hospital": item.hospital, "email": item.email}
                for item in hcps
            ]
    except Exception:
        pass
    finally:
        db.close()

    mock_hcps = [
        {"id": 1, "name": "Dr. Arjun Sharma", "specialty": "Oncology", "hospital": "Apollo Hospitals"},
        {"id": 2, "name": "Dr. Priya Mehta", "specialty": "Cardiology", "hospital": "AIIMS Delhi"},
        {"id": 3, "name": "Dr. Rajesh Kumar", "specialty": "Neurology", "hospital": "Fortis Healthcare"},
        {"id": 4, "name": "Dr. Anita Desai", "specialty": "Endocrinology", "hospital": "Narayana Health"},
        {"id": 5, "name": "Dr. Smith", "specialty": "General Medicine", "hospital": "City Medical Center"},
    ]
    if q:
        q_lower = q.lower()
        return [item for item in mock_hcps if q_lower in item["name"].lower()]
    return mock_hcps


@app.get("/health")
def health():
    return {"status": "ok", "service": "CRM HCP AI Backend", "database": ACTIVE_DATABASE_URL}
