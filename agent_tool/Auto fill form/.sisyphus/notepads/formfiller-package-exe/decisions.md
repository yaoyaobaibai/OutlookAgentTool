# FormFiller EXE Packaging - Decisions

## Architural Decisions
- **Packaging mode**: `--onedir` (folder output) — not `--onefile`
- **Console**: `--console` (keep console window)
- **Browser**: Use user's installed Chrome via `channel="chrome"` — no bundled Chromium
- **No code changes**: Use existing batch scripts as-is
