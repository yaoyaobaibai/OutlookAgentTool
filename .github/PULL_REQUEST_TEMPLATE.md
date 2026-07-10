# Pull Request

## Description

<!-- Briefly describe what this PR does and why. -->

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would change existing behavior)
- [ ] Documentation update
- [ ] Build/CI change

## Related Issue

<!-- Link to related issue(s): Fixes #123, Closes #456 -->

Fixes #

## Verification Checklist (MANDATORY)

### Code Quality
- [ ] `python -m py_compile` passes on all modified `.py` files
- [ ] No new `print()` calls with non-ASCII characters (cp1252 crash risk)
- [ ] All log messages use English ASCII only (--windowed EXE constraint)
- [ ] No "might be useful later" code — only what's needed now

### Project-Specific Checks (OutlookAgent)

#### P0 — MUST pass
- [ ] All `subprocess` calls include `creationflags=0x08000000` (no popup black windows)
- [ ] CSS processing order: clear old styles FIRST, then inject new ones (not reversed)
- [ ] If `_html_body_to_pdf` was modified in `attachment_handler.py` → same change applied to `msg_to_pdf.py`

#### P1 — Should pass
- [ ] `@page` CSS uses `mm` units, not `pt` (xhtml2pdf compatibility)
- [ ] Word COM code includes `taskkill /f /im WINWORD.EXE` cleanup
- [ ] Diagnostic logs appear BEFORE `_logging.disable(_logging.CRITICAL)`
- [ ] Excel COM code sets `ActivePrinter = "Microsoft Print to PDF"` before export

#### P2 — Nice to have
- [ ] Logo/attachment filter uses dual check: `hidden` attribute + `contentId` with image extension

### Build Verification (if applicable)
- [ ] EXE built successfully
- [ ] PDFMergeTool.exe ≈ 41MB, OutlookAgent.exe ≈ 38MB
- [ ] `%APPDATA%\pyinstaller` cache cleared before rebuild

## Screenshots / Logs

<!-- If applicable, add screenshots or log snippets to demonstrate the change. -->

## Breaking Changes

<!-- Describe any breaking changes and migration path if applicable. -->

## Additional Notes

<!-- Anything else reviewers should know. -->
