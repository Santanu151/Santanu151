from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class CallLog:
    call_id: str
    from_number: str
    to_number: str
    stage: str
    transcript: str
    created_at: str


class STTService:
    def transcribe(self, audio_url: str) -> str:
        # Stub: integrate Deepgram/Google/Azure here.
        return f"[transcript from {audio_url}]"


class TTSService:
    def synthesize(self, text: str) -> str:
        # Stub: integrate ElevenLabs/Azure/OpenAI TTS here.
        return f"[audio for: {text}]"


class LLMService:
    def draft_response(self, stage: str, transcript: str) -> str:
        # Stub: can be used for constrained augmentation; state machine stays source of truth.
        return f"Stage={stage}; heard={transcript}"


class CRMService:
    def upsert_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        # Stub: integrate HubSpot/Salesforce.
        return {"status": "ok", "lead": lead}


class SchedulerService:
    def create_hold(self, call_id: str, contact: str) -> Dict[str, Any]:
        # Stub: integrate Calendly or Google Calendar.
        return {
            "status": "scheduled",
            "call_id": call_id,
            "contact": contact,
            "slot": "next-available",
        }


class CallLogStore:
    def __init__(self) -> None:
        self._logs: list[CallLog] = []

    def append(self, call_id: str, from_number: str, to_number: str, stage: str, transcript: str) -> None:
        self._logs.append(
            CallLog(
                call_id=call_id,
                from_number=from_number,
                to_number=to_number,
                stage=stage,
                transcript=transcript,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        )

    def list_logs(self) -> list[CallLog]:
        return self._logs
