# Windows PC Smoke Test

Use this checklist on Windows 10/11 to confirm core flows work and there are no path/platform regressions.

## 1. Setup

PowerShell:

```powershell
cd "C:\path\to\labelMaker_ QR copy final copy NEW TEMPLATE"
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m py_compile app.py
```

Expected:
- `py_compile` finishes with no errors.

## 2. Run App

```powershell
python app.py
```

Open:
- `http://127.0.0.1:5000/`

Expected:
- Main UI loads.
- Store picker works.

## 3. Quick Endpoint Checks

In browser:
- `http://127.0.0.1:5000/health`
- `http://127.0.0.1:5000/test_upload.html`
- `http://127.0.0.1:5000/test_products.json`

Expected:
- `/health` returns healthy JSON.
- `/test_upload.html` renders (or returns a controlled 404 if not present).
- `/test_products.json` returns JSON (or controlled 404 if file not present).

## 4. Upload + Tag Load

1. Select a store.
2. Upload a known-good `.xlsx`.
3. Wait for processing to complete.
4. Confirm `CURRENT INVENTORY` list populates.
5. Search/filter once to verify controls are responsive.

Expected:
- No stuck spinner.
- No server traceback.
- Uploaded filename/session persists after refresh.

## 5. Generate Flow

1. Select at least 1 product.
2. Choose template (`Horizontal`, then `Vertical`, then `Mini`).
3. Click `Generate Tags`.
4. Download output.

Expected:
- DOCX generation succeeds for each tested template.
- No encoding/path errors in server logs.

## 6. Design Set / Template Controls

1. Toggle `Classic` and `User`.
2. Verify active state is visually obvious.
3. Verify spacing in Template Configuration is even.

Expected:
- Radio options are clearly visible in selected/unselected states.
- No jumpy layout or clipped controls.

## 7. Actions + Database Tools

1. Click `Undo`, `Redo`, `Clear & Reset` once each.
2. Run DB backup from UI.
3. (Optional) Restore from a backup file.

Expected:
- Actions respond without JS errors.
- Backup downloads successfully.
- Restore completes without path/permission errors.

## 8. CWD/Path Safety Check

Run app from a different working directory to confirm absolute path handling:

```powershell
cd $env:TEMP
python "C:\path\to\labelMaker_ QR copy final copy NEW TEMPLATE\app.py"
```

Expected:
- App still uses project `uploads` correctly.
- `test_upload.html` and `test_products.json` behavior remains correct.

## 9. Pass Criteria

Smoke test is a pass if all are true:
- App starts and loads on Windows.
- Upload + inventory + generation works.
- No uncaught exceptions in console during basic flows.
- Backup/restore endpoints work.
- No CWD-dependent breakage.

