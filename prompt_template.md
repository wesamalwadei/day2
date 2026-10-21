
# PROMPT TEMPLATE — CRUD API Builder (v1.1)

ROLE: You are a senior Python backend engineer who writes
production-quality, fully tested code.

TASK: Build a complete, runnable CRUD API for the entity below.

STACK: {{STACK}}
ENTITY: {{ENTITY}}
FIELDS: {{FIELDS}}
ENDPOINTS: {{ENDPOINTS}}
VALIDATION: {{VALIDATION_RULES}}
DATA: load {{SEED_FILE}} at startup
TESTS: {{TEST_REQUIREMENTS}}
CONSTRAINTS:
- Use Pydantic v2 only (field_validator, pattern=, model_dump); no v1 APIs.
- Use only fastapi, pydantic, uvicorn, pytest, httpx and the standard library.
- Tests must use asset_ids that exist in {{SEED_FILE}}; empty CSV cells (e.g. notes) must become None.

OUTPUT FORMAT: one fenced code block per file, preceded by the file
path. Files: main.py, models.py, test_api.py, README.md. No prose
between files.

DEFINITION OF DONE: `uvicorn main:app` starts; `pytest -q` passes;
no TODOs or placeholders.