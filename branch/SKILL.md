---
name: branch
description: Opens a "branch": a point of one conversation that will be resolved in another conversation, with a visible mark on both ends and a record in `tree.md`. Works in VS Code, the Claude desktop app and Claude Code on the web. Use when the user types `/branch` (with or without a pasted excerpt), says "open a branch" / "resolve this in another conversation", `/branch tree [point]` to branch straight from a point already in tree.md (skips the checklist and confirmation), `/branch close` / "close the branch" to finish one, or `/branch open N` / `/branch trunk` to open the conversation of a branch or of the trunk.
---

# Branch

A conversation is the **trunk**. A point in it that must be resolved separately becomes a **branch**, handled in a new conversation. Both ends are marked, and the map of everything lives in `tree.md`, at the project root.

## Environment

At the start of any command, run `python branch_link.py env` (this skill's `scripts/` folder). It answers:

- **`vscode`** (Claude Code extension): conversations open through extension links (`vscode://anthropic.claude-code/open`), with the opening text **pre-filled, not sent**: the user checks it and presses Enter. The link works from the terminal (`code --open-url`); **clicked inside the conversation panel it does nothing**, so never offer a clickable link in the chat.
- **`other`** (Claude desktop app, terminal): there are no links. Every "open" step becomes a **code block with the text to paste** into a new conversation (or into the trunk / branch conversation, for `close`), and the user opens it by hand.
- **`web`** (Claude Code on the web, in a cloud clone of the repository): same as `other`, and in addition every change to `tree.md` is **committed and pushed** right after it is written, or it is lost with the session.

If `python` is not available, treat it as `other` and take the session id from the conversation's own context, if known; otherwise leave `[id]`.

## `tree.md`

One file for all trees, with a fixed structure:

```markdown
# Tree

## 🌳 [New website: home page](vscode://anthropic.claude-code/open?session=<trunk id>) · 15/10 · `a1b2c3d4`
- [x] Define the color palette
- [ ] Logo size in the header
  - 🌿 **[Branch 1](vscode://anthropic.claude-code/open?session=<branch id>)**: logo proportion on mobile
    - Origin: "excerpt that generated the branch…"
- [ ] Heading typography
  - ✅ **Branch 2**: heading font
    - Conclusion: …
```

- **Tree** = `##` with 🌳, the theme, the opening date and the first 8 characters of the trunk id. In `vscode`, the theme is a link to the trunk session; elsewhere, plain text.
- **Checklist** = the still-open points of the theme, `- [ ]` / `- [x]`.
- **Branch** = item nested under the point it came from: 🌿 open, ✅ closed, numbered in tree order (1, 2, 3…). Branch of a branch: `1.1`, `1.2`, nested under the parent branch, which gets its own checklist by the same rule.
- **Branch link** (only in `vscode`): until the branch conversation has started, it is the opening link (`?prompt=`, new conversation with the text pre-filled); on `/branch continue`, it is replaced by the branch session link (`?session=`). Elsewhere, the branch has no link; `/branch continue` adds its 8-character id after the title, in backticks.
- Trees opened in one environment keep working in another: a link that cannot be used is just ignored, and the 8-character ids identify the conversations.
- No personal or sensitive data in the file or in the origin excerpt.

**Cleanup:** never automatic. When `/branch close` leaves a tree with **no open 🌿 branch**, ask the user, in the same confirmation as the conclusion, whether the tree should also leave `tree.md`. Only on a yes: if the project keeps a history log (a `LOG.md`, for example), write one line to it with the tree theme, its branches and the conclusion of each; then delete the tree. If the file ends up with no trees, only `# Tree` remains. On a no, the tree stays as it is, with every branch ✅.

## Session id and links

Everything through `scripts/branch_link.py`:

- `python branch_link.py env`: `vscode`, `web` or `other` (see above).
- `python branch_link.py session`: id of the current conversation (`CLAUDE_CODE_SESSION_ID`; failing that, the most recent `.jsonl` in the project's sessions folder, under `~/.claude/projects/`, or the one given with `--dir <path>` / `BRANCH_SESSIONS_DIR`).
- `python branch_link.py link --session <id>`: link that opens that conversation (`vscode` only).
- `python branch_link.py link --prompt-file <file>`: link that opens a new conversation with the file's text pre-filled (`vscode` only; write the text to a temporary file; the script handles encoding).
- `--open` on any `link`: also opens it in VS Code right away.

## `/branch` — open

1. **Origin point.** The excerpt pasted with the command. Without an excerpt, the most recent point under discussion; confirm which in one line.
2. **Does this conversation's tree already exist?** Get this session's id (`branch_link.py session`) **before** opening the branch conversation, which becomes the most recent session, and look for it in `tree.md`.
   - **No:** turn the session's open theme into a short checklist (only what is still at stake, one line per point; `[x]` on what the conversation already resolved) and identify which point the branch leaves from. Create the tree with that checklist.
   - **Yes:** do not redo the checklist. Mark `[x]` on what was resolved since last time, find the origin point (or add it, if new) and hang the branch on it.
   - **This conversation is itself a branch** (it opened with a branch's opening text): the new branch hangs on the current branch in the origin tree, numbered `N.1`, `N.2`…
3. **Confirm before writing.** Show the user the checklist as it will look (new, or the existing one with what changed) and the point the branch leaves from marked "← branch". Ask if it is ok or if anything changes, and wait for the answer. With an adjustment, show it again only if the change is big; otherwise write it already adjusted. Nothing goes into `tree.md` before this.
4. **Write** the branch to `tree.md`: 🌿, number, short title, an "Origin" line with the excerpt (up to ~200 characters, cut with "…"). In `web`, commit and push.
5. **Open the branch conversation.**
   - `vscode`: write the opening text (template below) to a temporary file and run `branch_link.py link --prompt-file <file> --open`. Save that link on the branch in `tree.md`.
   - `other` / `web`: show the opening text in a code block, to paste into a new conversation.
6. **Reply in conversation 1** with the mark:

   > 🌿 **Branch N opened:** [title] · from the point "[checklist point]". [vscode: The branch conversation opened with the text pre-filled: just check it and press Enter. · other/web: Open a new conversation and paste the text below.]

   If `--open` fails in `vscode`, fall back to the code block. Opening text:

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
4. **Open the conversation** as in step 5. The "Excerpt" line of the opening text is the point's text; the "Context" line is built from the tree itself (theme, the point, its sibling branches and their conclusions) plus anything the user said in the command. If this conversation is not the trunk, there is no trunk context to draw on: say in "Context" that the point comes from `tree.md`, and let the branch conversation read the trunk's repository files if it needs more.
5. **Reply** with the same mark as step 6 above.

## `/branch continue` — start of conversation 2

It is the text pasted into the new conversation. Open the reply with:

> ↳ **Branch N** of the tree "[theme]" · origin: "[checklist point]"

Get this session's id (`branch_link.py session`) and record it on the branch in `tree.md`: in `vscode`, replace the opening link with the session link (`?session=`); elsewhere, add the 8-character id after the title. In `web`, commit and push. Check that the branch is 🌿 and go straight into the subject.

## `/branch close`

Runs in the branch conversation.

1. Summarize the conclusion in 1–3 lines and confirm with the user. If this is the tree's last (or only) open branch, ask in the same message whether the tree should also be deleted from `tree.md` (see step 4).
2. In `tree.md`: 🌿 → ✅ and add the "Conclusion" line. The origin point only becomes `[x]` if the user confirms it was also resolved. In `web`, commit and push.
3. Generate the return text in a code block, for the user to paste into conversation 1. In `vscode`, also open conversation 1 with `branch_link.py link --session <trunk id> --open`; elsewhere, say which conversation it is (tree theme and 8-character trunk id).

   ```
   ✅ Branch N closed: [title]
   Conclusion: [1–3 lines]
   ```

4. If this was the last (or only) open branch of the tree, the step 1 confirmation also asks whether to delete the tree; apply the **cleanup** above only if the user says yes, and say what was done in one line.

## `/branch open N` and `/branch trunk`

In `vscode`, they open the conversation of branch N (or of the trunk) with `branch_link.py link --session <id> --open`, reading the id from `tree.md`. Elsewhere, they say which conversation it is (title, date and 8-character id) for the user to find it in the conversation list.

## What not to do

- Do not use `tree.md` as the project's task list: it is only the map of conversations. If a pending item or decision comes out of the branch, it goes wherever the project keeps those.
- Do not delete a tree that still has an open 🌿 branch, nor touch another conversation's tree beyond marking the branch this conversation closes.
