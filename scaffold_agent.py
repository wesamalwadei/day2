
import json, os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
llm = ChatOpenAI(base_url="https://openrouter.ai/api/v1",
                 api_key=os.environ["OPENROUTER_API_KEY"],
                 model="openai/gpt-4o-mini", temperature=0,
                 max_tokens=6000)

PROMPT_TEMPLATE = open("prompt_template.md", encoding="utf-8").read()   # your Lab 1.2 v1.1
REQUIRED = ["main.py", "index.html", "test_api.py", "README.md"]


class State(TypedDict):
    spec: str        # what to build
    plan: str        # file plan from the planner node
    files: dict      # path -> content
    errors: list     # verification findings
    attempts: int


def plan_node(state: State):
    r = llm.invoke(
        "You are a software planner. List the files (path + one-line "
        "purpose) for this project. Backend: FastAPI main.py, pytest "
        "test_api.py, README.md. Frontend: single index.html.\n"
        f"SPEC:\n{state['spec']}")
    return {"plan": r.content}


def generate_node(state: State):
    r = llm.invoke(
        f"{PROMPT_TEMPLATE}\n\nFILE PLAN:\n{state['plan']}\n"
        f"Known issues to fix: {state['errors']}\n"
        'Return STRICT JSON: {"files": {"path": "content", ...}}')
    txt = r.content.strip()
    txt = txt.removeprefix("```json").removeprefix("```").removesuffix("```")
    try:
        return {"files": json.loads(txt)["files"],
                "attempts": state["attempts"] + 1, "errors": []}
    except Exception as e:                       # error-recovery branch
        return {"attempts": state["attempts"] + 1,
                "errors": [f"bad JSON from model: {e}"]}


def write_node(state: State):
    for path, content in state["files"].items():
        full = os.path.join("scaffold_out", path)
        os.makedirs(os.path.dirname(full) or "scaffold_out", exist_ok=True)
        open(full, "w", encoding="utf-8").write(content)
    return {}


def verify_node(state: State):
    if state["errors"]:
        return {}                                # keep JSON error for router
    missing = [f for f in REQUIRED
               if not any(p.endswith(f) and c.strip()
                          for p, c in state["files"].items())]
    return {"errors": [f"missing or empty: {m}" for m in missing]}


def route(state: State):
    return "done" if (not state["errors"] or state["attempts"] >= 3) else "retry"


g = StateGraph(State)
g.add_node("plan", plan_node)
g.add_node("generate", generate_node)
g.add_node("write", write_node)
g.add_node("verify", verify_node)
g.add_edge(START, "plan")
g.add_edge("plan", "generate")
g.add_edge("generate", "write")
g.add_edge("write", "verify")
g.add_conditional_edges("verify", route, {"retry": "generate", "done": END})
app = g.compile()


if __name__ == "__main__":
    final = app.invoke({"spec": "Asset maintenance mini-app: FastAPI CRUD "
                        "backend over maintenance_assets.csv, plus a simple "
                        "index.html that lists flagged assets.",
                        "plan": "", "files": {}, "errors": [], "attempts": 0})
    print("attempts:", final["attempts"], "| errors:", final["errors"])
    print("written to scaffold_out/:", list(final["files"]))