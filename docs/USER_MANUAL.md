# AGT Label Maker — User Manual

This manual explains how to install, run, and use the AGT Label Maker web application for generating professional cannabis product labels from Excel inventory and optional JSON URLs.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation](#2-installation)
3. [Starting the Application](#3-starting-the-application)
4. [First-Time Setup: Store Selection](#4-first-time-setup-store-selection)
5. [Main Workflow: Creating Labels](#5-main-workflow-creating-labels)
6. [Uploading an Excel File](#6-uploading-an-excel-file)
7. [Matching Products from a JSON URL](#7-matching-products-from-a-json-url)
8. [Filtering and Selecting Tags](#8-filtering-and-selecting-tags)
9. [Generating and Downloading Labels](#9-generating-and-downloading-labels)
10. [Database and Data Tools](#10-database-and-data-tools)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Overview

**AGT Label Maker** is a web application that:

- **Loads product data** from store-specific Excel files or from the product database.
- **Matches products** from external JSON URLs (e.g., Cultivera inventory transfer URLs) to your Excel/database products.
- **Lets you select** which products (tags) to include using filters and checkboxes.
- **Generates label documents** (DOCX) in several templates: Horizontal, Vertical, Mini, Double, Preroll, and Inventory.

**Typical use:** Upload an Excel file (or use database-only), optionally match a JSON URL to pre-select products, filter/select tags, choose a template, then click **Generate Tags** to download a DOCX file of labels.

---

## 2. Installation

### Requirements

- Python 3.x
- Dependencies listed in `requirements.txt`

### Install Dependencies

**Option 1 — Automated (recommended):**

```bash
./install_requirements.sh
```

**Option 2 — Cross-platform:**

```bash
python3 install_requirements.py
```

**Option 3 — Manual:**

```bash
pip3 install --user -r requirements.txt
python3 patch_docxcompose.py   # if needed for docxcompose)
```

### Verify Installation

```bash
python3 -c 'import app; print("Ready to run")'
```

---

## 3. Starting the Application

### Run the app

From the project root directory:

```bash
python3 app.py
```

Or:

```bash
python app.py
```

### What you’ll see

- **Local access:**  
  `http://127.0.0.1:8001`  
  (Port may be 8001–8010 if 8001 is in use.)

- **Network access:**  
  The console will show a second URL, e.g.  
  `http://<your-machine-IP>:8001`  
  so other computers on the same network can open the app.

- **Restrict to this computer only:**  
  Before starting, set:  
  `export HOST=127.0.0.1`  
  Then run the app. It will only listen on localhost.

- **Custom port:**  
  `export FLASK_PORT=5001`  
  Then run the app.

### Open the app

In a browser, go to the URL printed in the console (e.g. `http://127.0.0.1:8001`). If others can’t connect, allow the app’s port in your firewall.

---

## 4. First-Time Setup: Store Selection

Before uploading files or generating labels, you must choose a **store**. Each store has its own Excel data and product database.

1. When you first open the app, a **store selection** modal appears.
2. Choose your store from the list, for example:
   - AGT Bothell  
   - AGT Burien  
   - AGT Goldbar  
   - AGT Lynnwood  
   - AGT Seattle  
   - AGT Shoreline  
   - AGT Walla Walla  
   - Test  
3. Click the store name. The page will reload with that store’s context.
4. Store choice is remembered for your session and can persist across reloads.

**Important:** You cannot upload an Excel file until a store is selected. The filename should match the selected store (e.g. a file for Bothell should indicate “Bothell” in the name).

---

## 5. Main Workflow: Creating Labels

High-level steps:

1. **Select store** (if not already selected).
2. **Load product data**  
   - Upload an Excel file **or**  
   - Rely on the product database (no file), **or**  
   - Use **Match JSON** to load and select products from a JSON URL.
3. **Refine the list** with filters (Vendor, Brand, Product Type, Lineage, Weight, Price, DOH, High CBD).
4. **Select tags** in the “Current Inventory” list (left). Selected items appear in “Selected” (right). Use “Select All” for a vendor/category if available.
5. **Choose a template** (Horizontal, Vertical, Mini, Double, Preroll, Inventory).
6. Click **Generate Tags**.
7. **Download** the generated DOCX when the process completes.

---

## 6. Uploading an Excel File

### When to upload

- You have a store-specific Excel inventory file (e.g. from your POS or export).
- You want labels to reflect that file’s products and data.

### Steps

1. Ensure the correct **store** is selected.
2. In the **filter bar** at the top, click **Upload Excel**.
3. In the file picker, select an **.xlsx** (or .xls) file whose name matches the selected store.
4. Wait for processing. The **file path / name** appears near the upload button (e.g. “No file uploaded” → your filename).
5. When loading finishes, **Current Inventory** (left column) fills with product tags. You can search, filter, and select from them.

### Rules

- Only **Excel** files (`.xlsx`, `.xls`) are accepted.
- The **filename** must be valid for the **selected store** (validation runs on upload).
- One file per store/session; a new upload replaces the previous one for that session.

### If you don’t upload

- You can still use **Match JSON** to pull products from a JSON URL; matching uses the product database when no Excel file is present (or in addition to it).
- You can also use **database-only** mode: no file, but product list comes from the store’s product database.

---

## 7. Matching Products from a JSON URL

This feature matches products from an external **JSON URL** (e.g. Cultivera inventory transfer) to your Excel/database products and can pre-select them for labels.

### When to use it

- You have a **JSON URL** that lists products (e.g. `https://files.cultivera.com/.../Cultivera_ORD-30063_422044.json`).
- You want to **match** those JSON products to your Excel/database and add them to **Selected** in one step.

### Steps

1. (Recommended) Have a **store** selected and, if you use Excel, an **Excel file already uploaded**.
2. In the filter bar, click **Match JSON**.
3. In the **JSON Product Matching** modal:
   - Paste the full JSON URL into the input (e.g. `https://...`).
   - Click **Match JSON**.
4. Wait for matching (can take up to about two minutes for large data). Progress may be reported in the modal or browser console.
5. When finished:
   - The modal shows how many products were matched and selected.
   - Matched products are added to **Selected** (right column).
   - **Current Inventory** may update to include any new tags from the match.
6. Close the modal and continue with filters/template and **Generate Tags** as needed.

### URL rules

- Must be **HTTP or HTTPS** (or `data:`). If you omit `https://`, the app may try to add it.
- The URL must return **inventory transfer / product list JSON** that the app can parse.

### Detailed match view

- Some flows offer a **detailed match** or “Before & After” view where you can review and **Accept** matches.
- Use **Accept All Matches** or per-item accept, then **Save** so the selection is applied.

### JSON inventory slips (separate feature)

- From **Data Tools** or the same area, you may see **JSON Inventory Slips**.
- There you paste a **JSON URL** and generate **inventory slip documents** (not the same as “Match JSON” for tag selection). Use that when you want slips from JSON rather than matching to Excel/database tags.

---

## 8. Filtering and Selecting Tags

### Layout

- **Left:** **Current Inventory** — list of product tags (from Excel and/or database, and after JSON match).
- **Center:** Template, **Generate Tags**, and controls (Undo, Redo, Clear, Export, Data & Analytics, Reset Cache, Lineage Editor).
- **Right:** **Selected** — tags chosen for label generation. You can reorder by dragging.

### Filters (top bar)

Use the dropdowns to narrow **Current Inventory**:

- **Vendor**  
- **Brand**  
- **Product Type**  
- **Lineage** (e.g. Sativa, Indica, Hybrid)  
- **Weight**  
- **Price**  
- **DOH Compliance**  
- **High CBD**

Changing a filter updates the list; you can combine several filters.

### Selecting tags

- **By hand:** In Current Inventory, **check** the products you want. They appear in **Selected**.
- **Select All:** If available for a vendor/category, use it to select a whole group.
- **Search:** Use the **Search** box above Current Inventory to find products by name or other text.
- **Selected list:** You can **drag** items in the Selected column to change order; order can affect layout in the generated document.

### Clearing and resetting

- **Clear & Reset** (or “Clear Filters”): Clears selected tags and resets filters so you can start a new selection.
- **Undo / Redo**: Reverses or re-applies the last selection change (e.g. move to selected).

---

## 9. Generating and Downloading Labels

### Before you generate

- At least one tag should be in **Selected** (right column).
- Choose the **template** you want.

### Template options

In the center column, use the **TEMPLATE** dropdown:

- **Horizontal** — horizontal layout.
- **Vertical** — vertical layout.
- **Mini** — smaller labels.
- **Double** — two-up or double layout.
- **Preroll** — for pre-roll products.
- **Inventory** — inventory-style layout.

### Generate

1. Set **TEMPLATE** to the desired layout.
2. Click **Generate Tags**.
3. Wait for generation (may take several seconds to minutes for large sets). A progress or status message may appear.
4. When done, the app will prompt or auto-download a **DOCX** file (e.g. “Labels.docx” or similar). Save it to your computer.

### After generation

- Use **Export Data** to download the **selected tags as Excel** (separate from the label DOCX).
- To change layout, change **TEMPLATE** and run **Generate Tags** again.

---

## 10. Database and Data Tools

Available from the center column or the **Data & Analytics**-style entry:

- **Export Data** — Download selected tags as an Excel file.
- **Data & Analytics** — Open the product database manager: browse products, run analytics, **Edit DB** (add/edit/delete products).
- **Reset Cache** — Clear cached data so the next load uses fresh data from Excel/database. Use if the list seems stale.
- **Lineage Editor** — Open the lineage/strain editor to manage strain names and lineage (e.g. Sativa/Indica/Hybrid) and related display.

### Database manager (Edit DB)

- View product table, search, and run analytics.
- **Edit** existing products (name, vendor, type, lineage, weight, price, DOH, etc.).
- **Add** new products and **Delete** ones you don’t need.
- Changes here affect what appears in Current Inventory and in matching (including JSON match).

### Backups and health

- From the database/analytics UI you may have options to **backup** the database, **restore** from backup, and check **database health**. Use these for safety and troubleshooting.

---

## 11. Troubleshooting

### Store / upload

- **“Please select a store before uploading”**  
  Choose a store from the modal first, then upload.

- **Upload rejected (filename/store)**  
  Ensure the Excel filename matches the selected store (e.g. contains “Bothell” for AGT Bothell). Use a valid `.xlsx`/`.xls` file.

### JSON match

- **“Please enter a JSON URL first”**  
  Paste a full URL (e.g. `https://files.cultivera.com/.../file.json`) in the JSON Match modal and click **Match JSON**.

- **Match fails or times out**  
  - Check that the URL is publicly reachable (open it in a browser).  
  - Large payloads can take 1–2 minutes; wait or try a smaller JSON.  
  - Ensure store is set and, if you use Excel, that the file is uploaded so matching has data to match against.

### Tags / generation

- **No tags in Current Inventory**  
  - Confirm store is selected.  
  - Upload an Excel file **or** ensure the product database has products for that store.  
  - Try **Reset Cache** and reload the page.

- **Generate does nothing or no download**  
  - Ensure at least one tag is in **Selected**.  
  - Check the browser’s download settings (allow downloads, no aggressive pop-up blocker).  
  - Check the app logs or browser console for errors.

### Performance and cache

- **Slow or stale data**  
  Use **Reset Cache**, then reload. For heavy use, restart the app.

- **Port already in use**  
  The app will try 8001–8010. Use the URL printed in the console (it will show the port actually used). Or set `FLASK_PORT` to a free port and restart.

### Network (other computers can’t connect)

- App binds to `0.0.0.0` by default. Use the **network URL** printed at startup (e.g. `http://<IP>:8001`).
- Allow the app’s port in your **firewall** (Windows/macOS/Linux).
- If still failing, try `HOST=127.0.0.1` only for local use and use port forwarding or a reverse proxy for remote access.

### Logs

- **Log viewer** (e.g. under **/logs** or linked from the UI) shows server-side logs.
- Browser **Developer Tools (F12)** → **Console** and **Network** help debug front-end and API errors.

---

## Quick Reference

| Task              | Action |
|-------------------|--------|
| Start app         | `python3 app.py` |
| Open app          | Browser → `http://127.0.0.1:8001` (or URL shown in console) |
| Select store      | Use modal on first load; required before upload |
| Load products     | **Upload Excel** or use **Match JSON** with a URL |
| Filter list       | Use Vendor, Brand, Product Type, Lineage, etc. |
| Select for labels | Check items in Current Inventory; see Selected on the right |
| Generate labels  | Pick **TEMPLATE** → **Generate Tags** → download DOCX |
| Export selection  | **Export Data** (Excel of selected tags) |
| Manage products   | **Data & Analytics** → Edit DB, backups, analytics |
| Fix stale data    | **Reset Cache** and/or reload page |

---

*For installation details see `INSTALLATION.md`. For performance and API behavior see `QUICK_START_GUIDE.md` and `api_endpoints_summary.md`.*
