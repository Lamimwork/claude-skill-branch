# Branch skill 🌳🌿

A skill for [Claude Code](https://claude.com/claude-code) that turns a conversation into a **checklist** and lets you resolve its points in **separate conversations** (branches), without losing the thread of the main conversation (the trunk).

Everything is recorded in a mind map, `tree.md`, which you open with the Markmap extension in VS Code and click to jump from one conversation to another.

```text
🌳 New website: home page             ← trunk conversation
├─ [x] Define the color palette
├─ [ ] Logo size in the header
│   └─ 🌿 Branch 1: logo proportion on mobile   ← separate conversation, open
└─ [ ] Heading typography
    └─ ✅ Branch 2: heading font                ← already resolved, with conclusion
```

## Requirements

- **VS Code** with the **Claude Code** extension (the `vscode://anthropic.claude-code/open` links open conversations in it).
- The `code` command on your PATH (the VS Code installer offers it; on Mac: *Shell Command: Install 'code' command in PATH*).
- **Python 3.8+**.
- The **Markmap** extension in VS Code, to view `tree.md` as a mind map (optional, but that's the fun part).

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
| `/branch` (or `/branch <excerpt>`) | trunk conversation | Builds the topic's checklist, shows it for your approval, records the branch in `tree.md` and opens a new conversation with the context pre-filled (just press Enter). |
| `/branch tree [point]` | any | Branches straight from a point already in `tree.md`, skipping the checklist and the confirmation. |
| `/branch continue` | branch conversation | Comes in the pre-filled text; links the new conversation to the map. |
| `/branch close` | branch conversation | Summarizes the conclusion, marks ✅ on the map and gives back the summary to paste into the trunk. |
| `/branch open N` / `/branch trunk` | any | Opens the conversation of branch N or of the trunk. |

When a tree has no open branch left, it leaves `tree.md` on its own.

## Notes

- A link clicked **inside the chat panel** does nothing; it works from the terminal (`code --open-url`) and when clicked in Markmap. The skill already uses the terminal.
- The script finds conversations in `~/.claude/projects/<project folder>/`. If it can't, pass `--dir <path>` or set `BRANCH_SESSIONS_DIR`.
- This skill was previously named `galho` (Portuguese for "branch"); the old Portuguese version is in the git history.
