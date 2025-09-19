import asyncio, json, pty, os, signal
import pexpect
from typing import Any
from agents import Agent, Runner, function_tool, RunContextWrapper, SQLiteSession

# One REPL per session_id
REPLS: dict[str, pexpect.spawn] = {}

def _key(ctx: RunContextWrapper[Any]) -> str:
    # session_id is set when you pass a Session to Runner.run(...)
    return getattr(ctx, "session_id", "default")

@function_tool
def repl_start(ctx: RunContextWrapper[Any], cmd: str = "/usr/local/cellar/open-adventure/1.20/bin/advent", cwd: str | None = None, timeout: float = 3.0) -> str:
    """
    Start (or restart) a TTY-backed REPL process and remember it for this session.

    Args:
      cmd: Command to run (e.g., "python3 -q", "node", "bash -i").
      cwd: Optional working directory.
      timeout: Seconds to wait for the initial prompt.
    """
    sid = _key(ctx)
    # Clean up any stale child
    if sid in REPLS:
        try: REPLS[sid].close(force=True)
        except Exception: pass

    child = pexpect.spawn(cmd, cwd=cwd, encoding="utf-8", timeout=timeout)
    # Make it look like a terminal
    child.setwinsize(40, 120)
    # Try to slurp whatever banner/prompt appears (best-effort)
    try:
        child.expect_exact([">>> ", "$ ", ">>>", "> ", "# ", "In [1]:", "\n"], timeout=timeout)
    except Exception:
        pass

    REPLS[sid] = child
    return f"started:{cmd}"

@function_tool
def repl_send(ctx: RunContextWrapper[Any], line: str, expect: str | None = None, timeout: float = 5.0) -> str:
    """
    Send one line to the REPL and return everything it printed since the last call.

    Args:
      line: A single line to send (no trailing newline needed).
      expect: Optional regex/prompt to wait for; if None, try common prompts.
      timeout: Seconds to wait for output before giving up.
    """
    sid = _key(ctx)
    if sid not in REPLS:
        return "error:repl_not_started"

    child = REPLS[sid]
    child.sendline(line)

    patterns = [expect] if expect else [
        r">>> |\.\.\. ",       # Python
        r"In \[\d+\]:|Out\[\d+\]:",  # IPython
        r"\$ |# |> |>>>",      # generic shells
        pexpect.EOF, pexpect.TIMEOUT
    ]
    try:
        child.expect(patterns, timeout=timeout)
    except pexpect.TIMEOUT:
        # Return whatever we have (non-blocking)
        return child.before or ""
    # child.before contains output since the send
    return child.before

@function_tool
def repl_stop(ctx: RunContextWrapper[Any]) -> str:
    """Terminate the REPL for this session."""
    sid = _key(ctx)
    ch = REPLS.pop(sid, None)
    if not ch:
        return "stopped:none"
    try:
        ch.sendeof()
    except Exception:
        pass
    try:
        ch.close(force=True)
    except Exception:
        pass
    return "stopped:ok"

# --- Wire up the Agent ---
agent = Agent(
    name="REPL proxy",
    instructions=(
        "You are a CLI REPL proxy. "
        "Call repl_start once, then use repl_send to run user code/commands, and repl_stop when done. "
        "Only return the REPL's output to the user."
    ),
    tools=[repl_start, repl_send, repl_stop],
)

async def main():
    # Use a session so the same REPL stays alive across turns
    session = SQLiteSession("demo-session")  # file-based persistence optional: SQLiteSession('demo','convos.db')

    print("Starting python REPL...")
    await Runner.run(agent, "Start a Python REPL.", session=session)
    out = await Runner.run(agent, "Run: print(3+2) and show only the number.", session=session)
    print(out.final_output)

    print("Stopping REPL...")
    await Runner.run(agent, "Stop the REPL.", session=session)

if __name__ == "__main__":
    asyncio.run(main())
