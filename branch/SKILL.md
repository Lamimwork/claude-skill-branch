---
name: branch
description: Opens a "branch": a point of one conversation that will be resolved in another conversation, with a visible link on both ends and a record in the `tree.md` mind map (Markmap). Use when the user types `/branch` (with or without a pasted excerpt), says "open a branch" / "resolve this in another conversation", `/branch tree [point]` to branch straight from a point already in tree.md (skips the checklist and confirmation), `/branch close` / "close the branch" to finish one, or `/branch open N` / `/branch trunk` to open the conversation of a branch or of the trunk.
---

# Branch

A conversation is the **trunk**. A point in it that must be resolved separately becomes a **branch**, handled in a new conversation. Both ends are marked, and the map of everything lives in `tree.md`, at the project root, to be viewed with the Markmap extension.

The new conversation opens through a link of the Claude Code extension for VS Code (`vscode://anthropic.claude-code/open`), with the opening text **pre-filled, not sent**: the user checks it and presses Enter. The link works from the terminal (`code --open-url`) and when clicked in Markmap; **clicked inside the conversation panel it does nothing**, so never offer a clickable link in the chat.

## `tree.md`

One file for all trees. Markmap draws headings and lists as branches, so the structure is fixed:

```markdown
# Tree

## 🌳 [New website: home page](vscode://anthropic.claude-code/open?session=<trunk id>) · 15/10 · `a1b2c3d4`
- [x] Define the color palette
- [ ] Logo size in the header
  - 🌿 **[Branch 1](vscode://anthropic.claude-code/open?session=<branch id>)**: logo proportion on mobile
    - Origin: "excerpt that generated the branch…"
- [ ] Heading typography
  - ✅ **[Branch 2](vscode://anthropic.claude-code/open?session=<branch id>)**: heading font
    - Conclusion: …
```

- **Tree** = `##` with 🌳, the theme as a link to the trunk session, the opening date and the first 8 characters of the id.
- **Checklist** = the still-open points of the theme, `- [ ]` / `- [x]`.
- **Branch** = item nested under the point it came from: 🌿 open, ✅ closed, numbered in tree order (1, 2, 3…). Branch of a branch: `1.1`, `1.2`, nested under the parent branch, which gets its own checklist by the same rule.
- **Branch link**: until the branch conversation has started, it is the opening link (`?prompt=`, new conversation with the text pre-filled); on `/branch continue`, it is replaced by the branch session link (`?session=`).
- No personal or sensitive data in the file or in the origin excerpt.

**Cleanup:** when a tree has **no open 🌿 branch**, the whole tree leaves `tree.md`. If the project keeps a history log (a `LOG.md`, for example), before deleting write one line to it: tree theme, branches and the conclusion of each. If the file ends up with no trees, only `# Tree` remains.

## Session id and links

Everything through `scripts/branch_link.py` (this skill's folder):

- `python branch_link.py session`: id of the current conversation (the most recent `.jsonl` in the project's sessions folder, under `~/.claude/projects/`). If it is not found, it accepts `--dir <path>` or the `BRANCH_SESSIONS_DIR` variable.
- `python branch_link.py link --session <id>`: link that opens that conversation.
- `python branch_link.py link --prompt-file <file>`: link that opens a new conversation with the file's text pre-filled (write the text to a temporary file; the script handles encoding).
- `--open` on any `link`: also opens it in VS Code right away.

## `/branch` — open

1. **Origin point.** The excerpt pasted with the command. Without an excerpt, the most recent point under discussion; confirm which in one line.
2. **Does this conversation's tree already exist?** Get this session's id (`branch_link.py session`) **before** opening the branch conversation, which becomes the most recent session, and look for it in `tree.md`.
   - **No:** turn the session's open theme into a short checklist (only what is still at stake, one line per point; `[x]` on what the conversation already resolved) and identify which point the branch leaves from. Create the tree with that checklist.
   - **Yes:** do not redo the checklist. Mark `[x]` on what was resolved since last time, find the origin point (or add it, if new) and hang the branch on it.
   - **This conversation is itself a branch** (it opened with a branch's opening text): the new branch hangs on the current branch in the origin tree, numbered `N.1`, `N.2`…
3. **Confirm before writing.** Show the user the checklist as it will look (new, or the existing one with what changed) and the point the branch leaves from marked "← branch". Ask if it is ok or if anything changes, and wait for the answer. With an adjustment, show it again only if the change is big; otherwise write it already adjusted. Nothing goes into `tree.md` before this.
4. **Write** the branch to `tree.md`: 🌿, number, short title, an "Origin" line with the excerpt (up to ~200 characters, cut with "…").
5. **Open the branch conversation**: write the opening text (template below) to a temporary file and run `branch_link.py link --prompt-file <file> --open`. Save that link on the branch in `tree.md`.
6. **Reply in conversation 1** with the mark:

   > 🌿 **Branch N opened:** [title] · from the point "[checklist point]". The branch conversation opened with the text pre-filled: just check it and press Enter.

   If `--open` fails, show the opening text in a code block to copy and paste into a new conversation. Opening text:

   ```
   /branch continue
   ↳ Branch N of the tree "[theme]" (session [8-character id])
   Origin point: [checklist point]
   Excerpt: "[excerpt]"
   Context: [2–4 lines on what is already known and what is left to resolve]
   ```

## `/branch tree [point]` — open from tree.md

For when the tree **already exists** in `tree.md` (made by hand, or by an earlier `/branch`) and the user wants to branch from one of its points. The tree and the checklist are already there, so **skip steps 2 and 3 above: no checklist is generated and nothing is confirmed**; go straight to writing the branch.

1. **Find the tree.** In order: the one whose trunk id matches this session (`branch_link.py session`); the only tree in the file; otherwise ask which one in one line. If `tree.md` has no tree, say so and fall back to plain `/branch`.
2. **Find the point.** `[point]` is a number (position among the tree's `- [ ]` points, counting top-down), a fragment of the text, or nothing. Without `[point]`, list the open `- [ ]` points of the tree, numbered, and ask which one. A fragment that matches two points: ask. If this conversation is itself a branch and the point lies in the tree of origin, the numbering follows the "branch of a branch" rule (`N.1`…); otherwise it takes the next free number in the tree.
3. **Write** the branch under that point exactly as in step 4 above. The "Origin" excerpt is the point's own text (plus the extra excerpt, if the user pasted one). Do not touch the other checklist lines.
4. **Open the conversation** as in step 5. The "Excerpt" line of the opening text is the point's text; the "Context" line is built from the tree itself (theme, the point, its sibling branches and their conclusions) plus anything the user said in the command. If this conversation is not the trunk, there is no trunk context to draw on: say in "Context" that the point comes from `tree.md`, and let the branch conversation read the project files if it needs more.
5. **Reply** with the same mark as step 6 above.

## `/branch continue` — start of conversation 2

It is the text pasted into the new conversation. Open the reply with:

> ↳ **Branch N** of the tree "[theme]" · origin: "[checklist point]"

Get this session's id (`branch_link.py session`) and, in `tree.md`, replace the branch's opening link with the session link (`?session=`). Check that the branch is 🌿 and go straight into the subject.

## `/branch close`

Runs in the branch conversation.

1. Summarize the conclusion in 1–3 lines and confirm with the user.
2. In `tree.md`: 🌿 → ✅ and add the "Conclusion" line. The origin point only becomes `[x]` if the user confirms it was also resolved.
3. Generate the return text in a code block, for the user to paste into conversation 1, and open conversation 1 with `branch_link.py link --session <trunk id> --open`:

   ```
   ✅ Branch N closed: [title]
   Conclusion: [1–3 lines]
   ```

4. If the tree is left with no open branch, apply the **cleanup** above and say so in one line.

## `/branch open N` and `/branch trunk`

They open the conversation of branch N (or of the trunk) with `branch_link.py link --session <id> --open`, reading the id from `tree.md`.

## What not to do

- Do not use `tree.md` as the project's task list: it is only the map of conversations. If a pending item or decision comes out of the branch, it goes wherever the project keeps those.
- Do not delete a tree that still has an open 🌿 branch, nor touch another conversation's tree beyond marking the branch this conversation closes.
