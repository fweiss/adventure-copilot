# production_cli.py
# pip install pexpect
import asyncio, os, re, signal, sys, time
from dataclasses import dataclass
from typing import Optional, Literal
from pexpect.replwrap import REPLWrapper

FENCE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

SYSTEM_PROMPT = """You are an execution agent controlling a live Python REPL.
Follow this protocol strictly:
- If another step is required, reply with EXACTLY ONE fenced code block ```python containing the FULL snippet to run.
- If you are completely done, reply with: FINAL: <concise answer>.
- Keep outputs small (print summaries).
- Never include text outside the single code block when you intend code execution.
"""

def extract_code_fence(text: str) -> Optional[str]:
    m = FENCE_RE.search(text)
    return m.group(1).strip() if m else None

@dataclass
class StepResult:
    done: bool
    code_executed: Optional[str] = None
    exec_output: Optional[str] = None
    final_text: Optional[str] = None

class Repl:
    def __init__(self):
        self.repl = self._spawn()

    def _spawn(self) -> REPLWrapper:
        return REPLWrapper(
            "python3 -q",
            r">>> ",
            prompt_change=None,
            continuation_prompt=r"\.\.\. "
        )

    def reset(self):
        try:
            self.repl.child.close(force=True)
        except Exception:
            pass
        self.repl = self._spawn()

    def run(self, code: str, timeout: float = 15.0) -> str:
        return self.repl.run_command(code + "\n", timeout=timeout).rstrip()

    def interrupt(self):
        # Send Ctrl-C to the child if supported
        try:
            self.repl.child.sendintr()
        except Exception:
            pass

class AgentRuntime:
    """
    Orchestrates model <-> REPL steps.
    Replace `self.llm()` with your actual LLM call (OpenAI, etc).
    """
    def __init__(self, repl: Repl, system_prompt: str = SYSTEM_PROMPT, max_steps: int = 6):
        self.repl = repl
        self.messages = [{"role":"system","content": system_prompt}]
        self.max_steps = max_steps

    def llm(self, messages: list[dict]) -> str:
        """
        TODO: Replace with your LLM client call.
        Must return either
          - a single fenced code block (```python ... ```) to execute, or
          - a line: 'FINAL: ...'
        """
        # Placeholder demo behavior:
        user_asks = messages[-1]["content"].lower()
        if "add" in user_asks and "2 and 2" in user_asks:
            return "```python\nprint(2+2)\n```"
        return "FINAL: I don’t have real LLM hooked up yet."

    def step(self, user_prompt: str, timeout: float = 15.0) -> StepResult:
        self.messages.append({"role":"user","content": user_prompt})
        assistant_text = self.llm(self.messages)

        # 1) Final?
        if assistant_text.strip().startswith("FINAL:"):
            final = assistant_text.strip()[6:].strip()
            self.messages.append({"role":"assistant","content": assistant_text})
            return StepResult(done=True, final_text=final)

        # 2) Code step?
        code = extract_code_fence(assistant_text)
        if not code:
            # Model didn't follow protocol; treat as final for safety.
            self.messages.append({"role":"assistant","content": assistant_text})
            return StepResult(done=True, final_text=assistant_text)

        # Execute
        try:
            output = self.repl.run(code, timeout=timeout)
        except Exception as e:
            output = f"[execution error] {e!r}"

        # Feed observation back to model for the next step
        self.messages.append({"role":"assistant","content": assistant_text})
        self.messages.append({"role":"user","content": f"Observation:\n{output}"})
        return StepResult(done=False, code_executed=code, exec_output=output)

async def main():
    repl = Repl()
    agent = AgentRuntime(repl)

    # Sync REPL and show banner/readiness
    ready = repl.run('print("READY")')
    print(f"[startup]\n{ready}\n")
    print("Commands: :exit, :reset, :interrupt, :timeout <sec>\n")

    timeout = 15.0
    while True:
        try:
            user = await asyncio.to_thread(input, "you> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user.strip() == ":exit":
            break
        if user.strip() == ":reset":
            repl.reset()
            print("[repl reset]\n")
            continue
        if user.strip().startswith(":timeout"):
            parts = user.split()
            if len(parts) == 2 and parts[1].isdigit():
                timeout = float(parts[1])
                print(f"[timeout set to {timeout}s]\n")
            else:
                print("[usage] :timeout 20\n")
            continue
        if user.strip() == ":interrupt":
            repl.interrupt()
            print("[interrupt sent]\n")
            continue

        # Multi-step controller
        for i in range(agent.max_steps):
            res = agent.step(user_prompt=user if i == 0 else "(continue)", timeout=timeout)
            if res.code_executed:
                print(f"\n[step {i+1} executed]\n{res.code_executed}\n")
                print(f"[output]\n{res.exec_output}\n")
            if res.done:
                print(f"[final]\n{res.final_text}\n")
                break
        else:
            print("[max steps reached]\n")

if __name__ == "__main__":
    asyncio.run(main())
