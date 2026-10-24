"""Environment, session id and Claude Code VS Code extension links, for the branch skill.

  python branch_link.py env                        vscode, web or other (where this conversation runs)
  python branch_link.py session                    id of the current conversation
  python branch_link.py link --session ID          link that opens a conversation
  python branch_link.py link --prompt-file FILE    link that opens a new conversation with the text pre-filled
  ... link [...] --open                            also opens it in VS Code (code --open-url)

The sessions folder is the one of the open project (current directory). To use another:
  --dir PATH, or the BRANCH_SESSIONS_DIR environment variable.

Links only exist in VS Code. The pre-filled text is not sent: the user checks it and presses Enter.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
BASE = "vscode://anthropic.claude-code/open"


def sessions_dir(path=None):
    """Folder where Claude Code stores the current project's conversations.

    Claude Code names the folder by replacing every character of the project path
    that is not a letter or digit with '-' (e.g. C:\\Users\\ana\\proj -> C--Users-ana-proj).
    """
    path = path or os.environ.get("BRANCH_SESSIONS_DIR")
    if path:
        return Path(path)
    name = re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
    if PROJECTS.is_dir():
        for p in PROJECTS.iterdir():
            if p.is_dir() and p.name.lower() == name.lower():
                return p
    return PROJECTS / name


def environment():
    if os.environ.get("CLAUDE_CODE_REMOTE"):
        return "web"
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT") == "claude-vscode":
        return "vscode"
    return "other"


def current_session(path=None):
    if not path and os.environ.get("CLAUDE_CODE_SESSION_ID"):
        return os.environ["CLAUDE_CODE_SESSION_ID"]
    folder = sessions_dir(path)
    files = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        sys.exit("No session found in " + str(folder) + " (use --dir or BRANCH_SESSIONS_DIR)")
    return files[0].stem


def build_link(session=None, prompt=None):
    params = {}
    if session:
        params["session"] = session
    if prompt:
        params["prompt"] = prompt
    return BASE + ("?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote) if params else "")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("env")
    ss = sub.add_parser("session")
    ss.add_argument("--dir")
    lk = sub.add_parser("link")
    lk.add_argument("--session")
    lk.add_argument("--prompt-file")
    lk.add_argument("--open", action="store_true")
    a = ap.parse_args()

    if a.cmd == "env":
        print(environment())
        return

    if a.cmd == "session":
        print(current_session(a.dir))
        return

    prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip() if a.prompt_file else None
    link = build_link(a.session, prompt)
    print(link)
    if a.open:
        code = shutil.which("code") or shutil.which("code.cmd")
        if not code:
            sys.exit("'code' command not found; open it from the link in tree.md.")
        subprocess.run([code, "--open-url", link], check=True)


if __name__ == "__main__":
    main()
