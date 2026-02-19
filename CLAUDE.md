# Boris Mode — Claude Code Operating System

## Default Workflow

1. **Plan Mode** — Start here. Do not write code yet.
2. **Produce a plan** containing:
   - Steps (numbered, small)
   - Files to create or change
   - Commands to run
   - Risks and how to mitigate them
   - Rollback strategy
   - Acceptance tests (what "done" looks like)
3. **Iterate** — Revise the plan until the user approves it.
4. **Implement** — Execute the approved plan exactly. No extras.
5. **Verify** — Run all verification commands. Fix failures. Rerun until green.
6. **Learn** — When a mistake repeats, add a rule to "Common mistakes" below.

## Hard Constraints

- Make the **smallest change that works**. Nothing more.
- No unrelated refactors, renames, or "while I'm here" changes.
- No new dependencies without explicit approval.
- Do not claim tests pass unless you actually ran them and saw the output.
- Do not modify files outside the scope of the approved plan.
- If something is unclear, ask — do not guess.

## Verification Commands

Edit these to match your project's tooling:

```bash
# Type checking
npm run typecheck

# Linting
npm run lint

# Tests
npm test
```

## Common Mistakes

- **Changing code outside the plan scope.** Stick to what was approved.
- **Skipping verification.** Always run typecheck, lint, and test after changes.
- **Adding imports or deps that weren't discussed.** Ask first.
- **Assuming a test passes without running it.** Run it. Paste the output.
- **Fixing lint errors by deleting code.** Fix the actual issue.
- **Making multiple unrelated changes in one commit.** One logical change per commit.
