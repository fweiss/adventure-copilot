import asyncio
from dataclasses import dataclass
from typing import Optional

import pexpect
from pexpect.replwrap import REPLWrapper

from agents import Agent, Runner, RunContextWrapper, function_tool, run_demo_loop

# ---------- Node REPL manager (pexpect) ----------

@dataclass
class AdventSession:
    repl: Optional[REPLWrapper] = None
    proc: Optional[pexpect.spawn] = None

    def start(self) -> None:
        # Start a fresh Node REPL
        # - 'node' uses '> ' as the prompt and '... ' for multiline continuation
        # - We don't change the prompt (prompt_change=None)
        self.proc = pexpect.spawn("/usr/local/cellar/open-adventure/1.20/bin/advent", encoding="utf-8", timeout=10)
        self.repl = REPLWrapper(self.proc, orig_prompt="> ", prompt_change=None, continuation_prompt="... ")
        # Small sanity check
        # _ = self.repl.run_command("process.version")

    def stop(self) -> None:
        if self.proc is not None:
            try:
                self.proc.sendline(".exit")
                self.proc.expect(pexpect.EOF, timeout=2)
            except Exception:
                try:
                    self.proc.terminate(force=True)
                except Exception:
                    pass
        self.repl = None
        self.proc = None

    def ensure_running(self) -> None:
        if self.repl is None or self.proc is None or not self.proc.isalive():
            self.stop()
            self.start()

    def eval(self, code: str) -> str:
        """
        Evaluate JavaScript in the Node REPL and return the REPL's textual output.
        """
        self.ensure_running()
        # REPLWrapper.run_command returns the text printed between prompts.
        # Node echoes results; errors also appear here.
        print("=====send: ", code)
        out = self.repl.run_command(code, timeout=15)
        print("=====reply: ", out.strip())
        return out.strip()


# A singleton session for this process
ADVENT = AdventSession()


# ---------- Agent tools ----------

@function_tool
def node_reset(ctx: RunContextWrapper[None]) -> str:
    """
    Restart the Node.js REPL subprocess. Use if the session gets into a bad state
    (e.g., infinite loop) or to clear context.
    """
    try:
        ADVENT.stop()
        ADVENT.start()
        return "Node REPL restarted."
    except Exception as e:
        return f"Failed to restart Node REPL: {e!r}"


@function_tool
def node_eval(ctx: RunContextWrapper[None], code: str) -> str:
    """
    Run JavaScript in the Node REPL and return the output as text.

    Args:
        code: JavaScript source to evaluate (single or multi-line).
    """
    try:
        ADVENT.ensure_running()
        return ADVENT.eval(code)
    except pexpect.TIMEOUT:
        return "Timed out waiting for REPL output. You may try node_reset()."
    except Exception as e:
        return f"REPL error: {e!r}"


# ---------- Agent definition & runner ----------

def build_agent() -> Agent:
    return Agent(
        name="Node-REPL Agent",
        instructions=(
            "You can execute game command inside a persistent adventure REPL.\n"
            "- start the game with the node_reset tool"
            "- when the game starts and asks `Would you like instructions`, answer 'y'"
            # "- start the game with the node_eval tool"
            # "- echo the output of the node_eval tool"
            "- send 'help' to node_eval to understand how to play the game"
            "- pass a user-input command to the game"
            "- use the navigation commands to go to different rooms\n"
            "- If evaluation stalls or the REPL looks broken, call node_reset.\n"
            "- remember the list of navigation commands needed to get to a particule room"
        ),
        tools=[node_eval, node_reset],
        # You can set a specific OpenAI model via `model=...` if needed.
    )

async def main() -> None:
    # Ensure REPL is up before starting
    ADVENT.start()
    agent = build_agent()
    # Quick interactive loop in your terminal
    await run_demo_loop(agent)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        ADVENT.stop()
