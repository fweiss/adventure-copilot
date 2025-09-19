# pip install pexpect
import asyncio, re
from pexpect.replwrap import REPLWrapper

SYSTEM_PROMPT = """
You are a coding agent controlling a live Python REPL.
- Always reply with EXACTLY ONE fenced code block labeled ```python containing the code to run.
- Never include commentary outside the fence.
- Keep outputs small (print summaries). If you need multiple steps, print intermediate results concisely.
- Stop when you've completed the user’s request.
"""

def extract_fenced_code(s: str, lang: str = "python") -> str | None:
    # Finds ```python ... ```
    m = re.search(rf"```{lang}\s*(.*?)```", s, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else None

class ReplAgent:
    def __init__(self):
        game="/usr/local/cellar/open-adventure/1.20/bin/advent"
        self.repl = REPLWrapper(game, orig_prompt=r"> ", prompt_change=None, continuation_prompt=r"\.\.\.")

    def run_repl(self, code: str, timeout: float = 15.0) -> str:
        # Send entire block; REPLWrapper runs until prompt reappears.
        print("=====Send code: ", code)
        return self.repl.run_command(code + "\n", timeout=timeout).rstrip()

async def llm_reply(messages: list[dict[str,str]]) -> str:
    """
    Replace this function with your LLM of choice.
    For now, it returns a trivial example that prints 2+2.
    messages = [{"role":"system","content":...}, {"role":"user","content":...}, {"role":"assistant","content":...}, ...]
    """
    return "```python\nprint(2+2)\n```"

async def run_conversation():
    agent = ReplAgent()
    messages = [{"role":"system","content": SYSTEM_PROMPT}]
    print("Type a natural-language request. :exit to quit.\n")
    while True:
        user = input("you> ").strip()
        if user == ":exit":
            break
        messages.append({"role":"user","content": user})

        # 1) Ask the LLM what to run
        assistant_text = await llm_reply(messages)
        code = extract_fenced_code(assistant_text, "python")
        if not code:
            print("(no runnable code block found)")
            continue

        # 2) Execute in REPL
        out = agent.run_repl(code)

        # 3) Show observation & feed it back if you want another step
        print(f"\n[exec output]\n{out}\n")
        messages.append({"role":"assistant","content": assistant_text})
        messages.append({"role":"user","content": f"Observation:\n{out}"})

if __name__ == "__main__":
    asyncio.run(run_conversation())
