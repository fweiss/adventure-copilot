# pip install pexpect
# (REPLWrapper is part of pexpect.replwrap)

import asyncio
import re
from pexpect.replwrap import REPLWrapper

# --- Utility ---------------------------------------------------------------

ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)

# --- Agent ----------------------------------------------------------------

class ReplAgent:
    """
    Wraps a REPLWrapper and exposes async methods.
    `respond()` is what the demo loop calls; inside, we delegate to run_command(),
    which delegates to REPLWrapper.run_command().
    """
    def __init__(self, repl: REPLWrapper, name: str = "py"):
        self.repl = repl
        self.name = name

    async def run_command(self, cmd: str, timeout: float = 15.0) -> str:
        # REPLWrapper.run_command is blocking; run it in a worker thread:
        raw = await asyncio.to_thread(self.repl.run_command, cmd, timeout=timeout)
        return strip_ansi(raw).rstrip()

    async def respond(self, user_input: str) -> str:
        """
        Add any planning/guardrails you want here.
        For demo, we just pass straight through to the REPL.
        """
        # Simple safety: ignore obviously destructive shell commands if we were a Bash agent.
        # For Python REPL this is mostly fine as-is.
        return await self.run_command(user_input)

# --- REPL constructors -----------------------------------------------------

def make_python_repl() -> REPLWrapper:
    # -q to quiet the banner; prompt regexes for primary/continuation prompts
    return REPLWrapper(
        "/usr/local/cellar/open-adventure/1.20/bin/advent",
        r"> ",
        prompt_change=None,
        continuation_prompt=r"\.\.\. "
    )

# If you want Bash instead, uncomment:
# def make_bash_repl() -> REPLWrapper:
#     # PS1 forces a predictable prompt; adjust to your shell if needed
#     return REPLWrapper(
#         command='bash --noprofile --norc -i',
#         prompt_regex=r"\$ ",
#         continuation_prompt_regex=None,
#         extra_init_cmd="PS1='$ '\n"
#     )

# --- Demo loop -------------------------------------------------------------

async def run_demo_loop(agent: ReplAgent) -> None:
    """
    Reads user input, sends it to agent.respond(), prints the REPL's output.
    Supports a simple multiline mode using triple quotes for Python blocks.
    Type :exit to quit.
    """
    # Sync to prompt & show we're ready (also surfaces any banner if present)
    ready = await agent.run_command('print("READY")')
    print(f"[startup]\n{ready}\n")

    print("Enter Python statements/expressions. Use triple quotes to send a multiline block.")
    print("Commands: :exit to quit, :help for help.\n")

    while True:
        # Non-blocking input via a thread:
        line = await asyncio.to_thread(input, f"{agent.name}> ")

        if line.strip() == ":exit":
            break
        if line.strip() == ":help":
            print("Type Python code and press Enter.\n"
                  "Multiline: start a line with ''' then finish the block with another ''' line.\n"
                  "Commands: :exit, :help\n")
            continue

        # Multiline block support: start with a line that's exactly '''.
        if line.strip() == "'''":
            print("(multiline mode, end with ''' on its own line)")
            lines = []
            while True:
                more = await asyncio.to_thread(input, "... ")
                if more.strip() == "'''":
                    break
                lines.append(more)
            block = "\n".join(lines) + "\n"
            out = await agent.respond(block)
        else:
            out = await agent.respond(line)

        if out:
            print(out)

# --- Main ------------------------------------------------------------------

async def main():
    py_repl = make_python_repl()
    agent = ReplAgent(py_repl, name="py")
    await run_demo_loop(agent)

if __name__ == "__main__":
    asyncio.run(main())
