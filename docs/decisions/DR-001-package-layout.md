# DR-001: Why use the src/<package>/ layout?

**Date:** 2026-10-17
**Phase:** 0 (Setup)
**Status:** Accepted

## Context
<!-- The situation BEFORE you chose:
     1. What happened in the project? 2. Why couldn't you leave it? 3. Why decide now? -->
When I set up the project, `uv init` automatically created a package folder at
`src/aml_transaction_monitoring/`, but I had also created loose folders like
`src/pipeline/` and `src/models/` directly under `src/`. This left two competing
structures in one project. Every future `import` depends on where the code lives,
so the structure had to be settled before writing real code. Deciding now is
cheap because the project has almost no code yet.

## Options considered
<!-- What realistic alternatives existed? Give each a fair pro and con. -->
| Option | Pros | Cons |
|---|---|---|
| A. Flat layout (package at project root) | Simplest structure, fewest folders | Python imports the local folder instead of the installed package, so packaging bugs can stay hidden |
| B. Loose folders under `src/` | Easy to start: just create folders | Imports become `from src.pipeline import ...`; "src" is a meaningless package name that can clash with other projects |
| C. `src/<package>/` layout | Python must use the installed package, so I test what others would get | One extra folder level; code only imports after the package is installed |

## Decision
<!-- Which option did you choose? One sentence. -->
Use option C: all code lives inside `src/aml_transaction_monitoring/`.

## Reason
<!-- WHY that option over the others? Most important reason first. -->
1. Because the code is not at the project root, Python cannot import it by accident
   from the current folder. It must use the installed package, so my tests and
   scripts run the same code anyone else would install.
2. It is the structure recommended by the Python Packaging User Guide and the one
   `uv` creates by default, so other engineers will recognise it immediately.

## Evidence
<!-- What can someone else check to confirm this? A source, experiment, or observation. -->
- Python Packaging User Guide, "src layout vs flat layout".
- Observed: after restructuring, `uv run python -m aml_transaction_monitoring.pipeline.spark_check`
  ran successfully, confirming imports resolve through the installed package.

## Trade-offs accepted
<!-- What does this choice cost you? Why is that acceptable? -->
- One extra folder level, so file paths are slightly longer.
- The package must be installed before imports work. `uv` does this automatically,
  so the practical cost is small.

## When I would revisit this
<!-- In what situation would a different option be the better choice? -->
For a single-file script or a throwaway experiment that will never be installed,
tested, or shared, a flat layout is simpler and the src layout adds structure
with no benefit.

## Explain it three ways
<!-- Same decision, three audiences, three depths. -->
- **To a compliance manager (no jargon):** It's like keeping the approved version of
  a policy in the official records system instead of a draft on someone's desk.
  Everyone, including me, always works from the official copy, so nobody relies on
  something that hasn't been properly filed.
- **To a data scientist:** The src layout forces imports to resolve through the
  installed package rather than the working directory, so tests exercise exactly
  what gets distributed and packaging errors surface early.
- **If asked "why?" three times:**
  Why the src layout? → So imports use the installed package.
  Why does that matter? → Otherwise tests can pass on my laptop while the installed version is broken.
  Why would it be broken? → Packaging can leave files out, and the flat layout hides that by importing the local folder.