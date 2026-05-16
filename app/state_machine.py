from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class CallStage(str, Enum):
    INTRO = "intro"
    QUALIFY = "qualify"
    OBJECTION = "objection"
    BOOKING = "booking"
    HANDOFF = "handoff"
    END = "end"


@dataclass
class CallContext:
    lead_name: str = "there"
    company: str = ""
    qualified: bool | None = None
    objections: List[str] = field(default_factory=list)
    meeting_booked: bool = False
    requested_human: bool = False
    do_not_call: bool = False


@dataclass
class StateMachineResult:
    stage: CallStage
    reply: str
    should_hangup: bool = False


class CallStateMachine:
    """Deterministic call flow to keep behavior predictable and auditable."""

    def __init__(self) -> None:
        self.stage = CallStage.INTRO

    def next(self, ctx: CallContext, user_utterance: str) -> StateMachineResult:
        normalized = user_utterance.lower().strip()

        if self._is_opt_out(normalized):
            ctx.do_not_call = True
            self.stage = CallStage.END
            return StateMachineResult(
                stage=self.stage,
                reply="Understood. I will add you to our do-not-call list. Goodbye.",
                should_hangup=True,
            )

        if self._requests_human(normalized):
            ctx.requested_human = True
            self.stage = CallStage.HANDOFF
            return StateMachineResult(
                stage=self.stage,
                reply="Absolutely. I can connect you with a human specialist now.",
            )

        if self.stage == CallStage.INTRO:
            self.stage = CallStage.QUALIFY
            return StateMachineResult(
                stage=self.stage,
                reply=(
                    f"Hi {ctx.lead_name}, I am calling from {ctx.company or 'our team'}. "
                    "Is now a bad time for a 30-second question?"
                ),
            )

        if self.stage == CallStage.QUALIFY:
            if any(x in normalized for x in ["yes", "sure", "okay", "ok"]):
                ctx.qualified = True
                self.stage = CallStage.BOOKING
                return StateMachineResult(
                    stage=self.stage,
                    reply=(
                        "Great. We help teams increase booked appointments. "
                        "Would you like a short demo next week?"
                    ),
                )
            ctx.qualified = False
            self.stage = CallStage.OBJECTION
            return StateMachineResult(
                stage=self.stage,
                reply="No problem. May I ask what is your top concern right now?",
            )

        if self.stage == CallStage.OBJECTION:
            ctx.objections.append(user_utterance)
            self.stage = CallStage.BOOKING
            return StateMachineResult(
                stage=self.stage,
                reply="Thanks for sharing. If we can solve that, should we schedule a 15-minute call?",
            )

        if self.stage == CallStage.BOOKING:
            if any(x in normalized for x in ["yes", "book", "schedule", "works"]):
                ctx.meeting_booked = True
                self.stage = CallStage.END
                return StateMachineResult(
                    stage=self.stage,
                    reply="Perfect. I have noted your interest and will send a calendar invite. Thank you.",
                    should_hangup=True,
                )
            self.stage = CallStage.END
            return StateMachineResult(
                stage=self.stage,
                reply="No worries. Thank you for your time today. Goodbye.",
                should_hangup=True,
            )

        if self.stage == CallStage.HANDOFF:
            return StateMachineResult(
                stage=self.stage,
                reply="Please hold while I transfer you.",
            )

        return StateMachineResult(
            stage=CallStage.END,
            reply="Goodbye.",
            should_hangup=True,
        )

    @staticmethod
    def _requests_human(text: str) -> bool:
        return any(x in text for x in ["human", "person", "agent", "representative"])

    @staticmethod
    def _is_opt_out(text: str) -> bool:
        return any(x in text for x in ["do not call", "stop calling", "remove me"])
