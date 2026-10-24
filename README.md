# Branch skill 🌳🌿

A skill for [Claude Code](https://claude.com/claude-code) that turns a conversation into a **checklist** and lets you resolve its points in **separate conversations** (branches), without losing the thread of the main conversation (the trunk).

Everything is recorded in `tree.md`, a plain Markdown map of your trees, their checklists and their branches.

It works wherever Claude Code runs: the VS Code extension, the Claude desktop app, the terminal and Claude Code on the web. The skill detects where it is running and adapts.

```text
🌳 New website: home page             ← trunk conversation
├─ [x] Define the color palette
├─ [ ] Logo size in the header
│   └─ 🌿 Branch 1: logo proportion on mobile   ← separate conversation, open
└─ [ ] Heading typography
    └─ ✅ Branch 2: heading font                ← already resolved, with conclusion
```

## Requirements

- **Claude Code**, in any of its forms.
- **Python 3.8+**, for the helper script (without it, the skill still works, just without detecting the environment).

## Where it runs

| Environment | How conversations open | `tree.md` |
| --- | --- | --- |
| **VS Code** (Claude Code extension) | Automatically, through `vscode://anthropic.claude-code/open` links, with the opening text pre-filled (just press Enter). Needs the `code` command on your PATH. | Trees and branches carry links to their conversations. |
| **Desktop app / terminal** | The skill gives you the opening text in a code block; you paste it into a new conversation. | No links; conversations are identified by their 8-character id. |
| **Claude Code on the web** | Same as the desktop app. | Same, and every change is committed and pushed, since the cloud clone does not outlive the session. |

Trees made in one environment keep working in another.

## Installation

Copy the `branch/` folder to one of these:

- `~/.claude/skills/branch/` — available in all your projects;
- `<your project>/.claude/skills/branch/` — only in that project.

```bash
git clone https://github.com/Lamimwork/claude-skill-branch.git
cp -r claude-skill-branch/branch ~/.claude/skills/
```

## Usage

| Command | Where | What it does |
| --- | --- | --- |
| `/branch` (or `/branch <excerpt>`) | trunk conversation | Builds the topic's checklist, shows it for your approval, records the branch in `tree.md` and opens a new conversation with the context (pre-filled in VS Code; to paste elsewhere). |
| `/branch tree [point]` | any | Branches straight from a point already in `tree.md`, skipping the checklist and the confirmation. |
| `/branch continue` | branch conversation | Comes in the opening text; links the new conversation to the map. |
| `/branch close` | branch conversation | Summarizes the conclusion, marks ✅ on the map and gives back the summary to paste into the trunk. |
| `/branch open N` / `/branch trunk` | any | Opens the conversation of branch N or of the trunk. |

When a tree has no open branch left, the skill asks whether to remove it from `tree.md`.

## Notes

- In VS Code, a link clicked **inside the chat panel** does nothing; it works from the terminal (`code --open-url`), which is what the skill uses.
- The script reads the session id from `CLAUDE_CODE_SESSION_ID`; failing that, it looks in `~/.claude/projects/<project folder>/`. If it can't find it, pass `--dir <path>` or set `BRANCH_SESSIONS_DIR`.
- This skill was previously named `galho` (Portuguese for "branch"); the old Portuguese version is in the git history.
