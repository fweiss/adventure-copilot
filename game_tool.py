# game_tool.py
import os, pexpect, re, time
from typing import Optional

class GameSession:
    def __init__(self, cmd: list[str], prompt_regex: str, timeout: float = 5.0, encoding="utf-8"):
        self.prompt = re.compile(prompt_regex, re.MULTILINE)
        self.child = pexpect.spawnu(" ".join(cmd), timeout=timeout, encoding=encoding)
        self.child.delaybeforesend = 0  # snappy input
        self._drain_banner()

    def _read_until_prompt(self) -> str:
        """Read until prompt or EOF/timeout; return whatever we got."""
        buf = []
        start = time.time()
        while True:
            try:
                chunk = self.child.read_nonblocking(size=1024, timeout=0.2)
                buf.append(chunk)
                if self.prompt.search("".join(buf)):
                    break
            except pexpect.TIMEOUT:
                # soft timeout: if we've already read something, return it
                if (time.time() - start) > self.child.timeout:
                    break
            except pexpect.EOF:
                break
        return "".join(buf)

    def _drain_banner(self) -> str:
        # Grab the initial splash screen/opening text
        try:
            time.sleep(0.1)
            return self._read_until_prompt()
        except Exception:
            return ""

    def send(self, line: str) -> str:
        if not line.endswith("\n"):
            line += "\n"
        self.child.send(line)
        # Some games echo; a short pause helps coalesce output
        time.sleep(0.05)
        out = self._read_until_prompt()
        # optional: trim ANSI codes if your game uses color
        return out

# Singleton-ish session for the process lifetime
_game: Optional[GameSession] = None

def get_game() -> GameSession:
    global _game
    if _game is None:
        _game = GameSession(
            cmd=["./your_game_binary"],          # e.g., "./adventure"
            prompt_regex=r"\n?>\s*$",            # e.g., lines ending with ">"
            timeout=6.0
        )
    return _game

# ---- Tool entrypoint the agent will call
def game_io(command: str) -> dict:
    """
    Sends a command to the game and returns the resulting text block.
    Return shape is a dict to stay friendly with tool schemas.
    """
    session = get_game()
    text = session.send(command)
    # Safety: truncate huge blobs
    if len(text) > 20000:
        text = text[:20000] + "\n...[truncated]..."
    return {"output": text}
