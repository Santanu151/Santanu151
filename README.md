# AI Cold Calling Agent (State-Machine Based)

This repository scaffolds a simple architecture for an AI cold-calling system:

`Twilio webhook -> Orchestrator service -> STT/TTS + LLM -> CRM + Scheduler -> Call logs dashboard`

## What is implemented

- **Twilio webhook entrypoint** at `POST /twilio/webhook`.
- **Orchestrator** in FastAPI (`app/main.py`) that coordinates services.
- **Deterministic state machine** (`app/state_machine.py`) for predictable call flow.
- **Service stubs** (`app/services.py`) for STT/TTS/LLM/CRM/Scheduler.
- **Call logs endpoint** at `GET /calls/logs`.

## Call stages

1. `intro`
2. `qualify`
3. `objection`
4. `booking`
5. `handoff`
6. `end`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Example request

```bash
curl -X POST http://127.0.0.1:8000/twilio/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call-001",
    "from_number": "+15551234567",
    "to_number": "+15557654321",
    "lead_name": "Alex",
    "company": "DemoCo",
    "transcript": "yes"
  }'
```

## Notes

- This is a baseline scaffold intended for extension.
- Real compliance enforcement (TCPA/DNC/recording consent, timezone windows) should be added before production.
- Replace service stubs with provider SDK integrations.
