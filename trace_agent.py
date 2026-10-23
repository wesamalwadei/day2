
import csv, json, os, datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url="https://openrouter.ai/api/v1",
                api_key=os.environ["OPENROUTER_API_KEY"])
MODEL = "openai/gpt-4o-mini"

with open("maintenance_assets.csv", newline="", encoding="utf-8") as f:
    ASSETS = list(csv.DictReader(f))

TRACE_FILE = "trace.jsonl"


def log(step, kind, content):
    rec = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "step": step, "type": kind, "content": content}
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def search_assets(status=None, criticality=None, asset_type=None, location=None):
    rows = ASSETS
    for key, val in [("status", status), ("criticality", criticality),
                     ("asset_type", asset_type), ("location", location)]:
        if val:
            rows = [r for r in rows if val.lower() in r[key].lower()]
    return rows[:20]


TOOLS = [{"type": "function", "function": {
    "name": "search_assets",
    "description": "Search the plant asset maintenance records.",
    "parameters": {"type": "object", "properties": {
        "status": {"type": "string"}, "criticality": {"type": "string"},
        "asset_type": {"type": "string"}, "location": {"type": "string"}}}}}]

SYSTEM = ("You are a plant maintenance assistant agent. Before every "
          "tool call, output one line starting with THOUGHT: explaining "
          "why. Use search_assets to answer. Cite asset_ids. "
          "If the records cannot answer, say so.")


def run_agent(question):
    log(0, "task", question)
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    for step_n in range(1, 6):
        r = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS)
        msg = r.choices[0].message
        messages.append(msg)
        if msg.content:
            log(step_n, "thought", msg.content)
        if not msg.tool_calls:
            log(step_n, "final_answer", msg.content)
            return msg.content
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            log(step_n, "action",
                {"tool": call.function.name, "args": args})
            result = search_assets(**args)
            log(step_n, "observation",
                {"rows_returned": len(result)})
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    return "Step limit reached."


if __name__ == "__main__":
    while True:
        q = input("\nAsk about plant assets (or exit): ")
        if q.strip().lower() == "exit":
            break
        print(run_agent(q))
        