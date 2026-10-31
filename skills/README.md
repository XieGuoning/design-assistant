# Skills

Agent skills vendored from [anthropics/skills](https://github.com/anthropics/skills) (checked 2026-10-31), in the standard `SKILL.md` format used by Claude Code, Codex and other agents.

| Skill | What it does |
|---|---|
| `frontend-design` | Distinctive, non-templated UI design: palette, typography, layout |
| `webapp-testing` | Test local web apps with Playwright (screenshots, console logs, UI behaviour) |
| `theme-factory` | Ten colour/font themes to apply consistently to decks, docs and HTML |
| `canvas-design` | Static visual art (posters, one-page designs) as PNG/PDF from a design philosophy |
| `mcp-builder` | Plan, build and evaluate MCP servers in Python or TypeScript |
| `skill-creator` | How to write and iteratively improve skills themselves |

Notes:

- To make an agent auto-discover a skill, copy or symlink its folder into `.claude/skills/` (Claude Code) or the equivalent skills directory of your agent.
- Two binary payloads from the originals are not vendored here because this import carried text files only: the `canvas-design` font files (`canvas-fonts/`, ~5.6 MB), so `canvas-design` is vendored as `SKILL.md` + `LICENSE.txt` only, and `theme-factory/theme-showcase.pdf`. Fetch them from the upstream repo if you need the full packages.
- `canvas-design/SKILL.md` carries one softened sentence versus upstream: a line that framed a refinement demand as a user quote now reads as a plain instruction. Everything else is verbatim, including each skill's `LICENSE.txt`.
