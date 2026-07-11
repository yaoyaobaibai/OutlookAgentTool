# Building v1.3.0 Release Artifacts

## Rebuild PRPOAgent.exe (with Mail Agent)

```powershell
$env:PATH = "C:\msys64\mingw64\bin;" + $env:PATH
Set-Location agent_tool\pr_po_agent
Remove-Item -Force -Recurse dist, build -ErrorAction SilentlyContinue
Remove-Item -Force -Recurse __pycache__, agents\__pycache__, agents\mail_agent\__pycache__, ui\__pycache__ -ErrorAction SilentlyContinue

pyinstaller --onefile --windowed --name "PRPOAgent" --paths . `
  --hidden-import=tkinter --hidden-import=pystray --hidden-import=PIL `
  --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw `
  --hidden-import=config --hidden-import=tray `
  --hidden-import=ui.main_window --hidden-import=ui.settings_dialog --hidden-import=ui.confirm_dialog `
  --hidden-import=agents --hidden-import=agents.mail_agent `
  --hidden-import=agents.mail_agent.rules_engine `
  --hidden-import=agents.mail_agent.inbox_writer `
  --hidden-import=agents.mail_agent.monitor `
  --hidden-import=agents.mail_agent.__main__ `
  main.py

# Copy to release package
$built = "agent_tool\pr_po_agent\dist\PRPOAgent.exe"
Copy-Item -Force $built "agent_tool\release_package\v1.3.0\PRPOAgent.exe"
```

Expected size: ~22 MB (includes Mail Agent modules)

## Rebuild ZIP

```powershell
$zip = "agent_tool\release_package\OutlookAgent_v1.3.0.zip"
Remove-Item -Force $zip -ErrorAction SilentlyContinue
Add-Type -AssemblyName "System.IO.Compression.FileSystem"
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    "agent_tool\release_package\v1.3.0\",
    $zip)
```

Expected size: ~134 MB

## Upload to GitHub Release

```bash
gh release upload v1.3.0 agent_tool\release_package\OutlookAgent_v1.3.0.zip --clobber
```

## Verifying Built EXE contains Mail Agent

```powershell
Select-String -Path agent_tool\release_package\v1.3.0\PRPOAgent.exe `
  -Pattern "mail_agent\.monitor" -SimpleMatch
# Should return at least one match
```

## Last Build Reference

- Date: 2026-07-10
- PRPOAgent.exe size: 22.27 MB
- MD5: b003d1d085fbe1d9fd0f5f1645d93c21
- Bundles: d8abee9 (Mail Agent MVP)
