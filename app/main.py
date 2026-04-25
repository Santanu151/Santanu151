from __future__ import annotations

from typing import Dict
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.services import CRMService, CallLogStore, LLMService, STTService, SchedulerService, TTSService
from app.state_machine import CallContext, CallStage, CallStateMachine

app = FastAPI(title="AI Cold Calling Agent", version="0.1.0")

stt = STTService()
tts = TTSService()
llm = LLMService()
crm = CRMService()
scheduler = SchedulerService()
logs = CallLogStore()

calls: Dict[str, dict] = {}


class TwilioWebhookPayload(BaseModel):
    call_id: str = Field(default_factory=lambda: str(uuid4()))
    from_number: str
    to_number: str
    lead_name: str = "there"
    company: str = ""
    transcript: str = ""


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/twilio/webhook")
def twilio_webhook(payload: TwilioWebhookPayload) -> dict:
    state = calls.get(payload.call_id)
    if state is None:
        sm = CallStateMachine()
        ctx = CallContext(lead_name=payload.lead_name, company=payload.company)
        calls[payload.call_id] = {"sm": sm, "ctx": ctx, "from": payload.from_number, "to": payload.to_number}
    else:
        sm = state["sm"]
        ctx = state["ctx"]

    result = sm.next(ctx, payload.transcript)
    ai_hint = llm.draft_response(result.stage.value, payload.transcript)
    audio_ref = tts.synthesize(result.reply)

    if result.stage == CallStage.BOOKING and ctx.qualified:
        scheduler.create_hold(payload.call_id, payload.from_number)

    crm.upsert_lead(
        {
            "phone": payload.from_number,
            "name": ctx.lead_name,
            "qualified": ctx.qualified,
            "meeting_booked": ctx.meeting_booked,
            "requested_human": ctx.requested_human,
            "do_not_call": ctx.do_not_call,
        }
    )

    logs.append(
        call_id=payload.call_id,
        from_number=payload.from_number,
        to_number=payload.to_number,
        stage=result.stage.value,
        transcript=payload.transcript,
    )

    return {
        "call_id": payload.call_id,
        "stage": result.stage.value,
        "say": result.reply,
        "audio_ref": audio_ref,
        "llm_hint": ai_hint,
        "hangup": result.should_hangup,
    }


@app.get("/calls/logs")
def call_logs() -> list[dict]:
    return [log.__dict__ for log in logs.list_logs()]
