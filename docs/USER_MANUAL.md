# AGT Designer  
## User Manual

**Document version:** 1.1  
**Application:** AGT Designer — Professional Cannabis Label Generation  
**Last updated:** 2026

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
12. [Quick Reference](#12-quick-reference)
13. [Advanced: QR Codes, Preroll Template, and Product Data](#13-advanced-qr-codes-preroll-template-and-product-data)

---

## 1. Overview

AGT Designer is a web application for generating professional cannabis product labels. It uses store-specific Excel files and/or a product database, and can match products from external JSON URLs (e.g., Cultivera inventory transfers).

### What the application does

| Function | Description |
|----------|-------------|
| **Load product data** | From store-specific Excel files or the product database. |
| **Match products** | From external JSON URLs (e.g., Cultivera) to your Excel/database products. |
| **Select products** | Use filters and checkboxes to choose which products (tags) to include. |
| **Generate labels** | Produce DOCX label documents in multiple templates. |

### Available label templates

Horizontal • Vertical • Mini • Double • Preroll • Inventory

### Typical workflow

1. Select a store.  
2. Load data (upload Excel, use database only, or match a JSON URL).  
3. Filter and select the tags you want.  
4. Choose a template and click **Generate Tags**.  
5. Download the generated DOCX file.

---

## 2. Installation

### 2.1 Requirements

- **Python:** 3.x  
- **Dependencies:** As listed in `requirements.txt`

### 2.2 Install dependencies

Choose one method.

| Method | Command |
|--------|--------|
| **Automated (recommended)** | `./install_requirements.sh` |
| **Cross-platform** | `python3 install_requirements.py` |
| **Manual** | `pip3 install --user -r requirements.txt` then `python3 patch_docxcompose.py` if needed |

### 2.3 Verify installation

Run:

```
python3 -c 'import app; print("Ready to run")'
```

If you see **Ready to run**, the installation is successful.

---

## 3. Starting the Application

### 3.1 Run the application

From the project root directory:

```
python3 app.py
```

or

```
python app.py
```

### 3.2 URLs and access

After startup, the console will display:

| Access type | URL example | Notes |
|-------------|-------------|--------|
| **Local (this computer)** | `http://127.0.0.1:8001` | Port may be 8001–8010 if 8001 is in use. |
| **Network (other devices)** | `http://<your-IP>:8001` | Shown in console; allow the port in your firewall if needed. |

### 3.3 Optional settings

| Goal | Action |
|------|--------|
| Restrict to this computer only | Before starting: `export HOST=127.0.0.1` then run the app. |
| Use a different port | Before starting: `export FLASK_PORT=5001` (or another free port) then run the app. |

### 3.4 Open the application

In a web browser, go to the URL shown in the console (e.g. `http://127.0.0.1:8001`). If other computers cannot connect, allow the application’s port in your firewall.

---

## 4. First-Time Setup: Store Selection

A **store** must be selected before uploading files or generating labels. Each store has its own Excel data and product database.

### Procedure: Select a store

1. Open the application.  
2. When the **store selection** modal appears, choose your store from the list.  
3. Click the store name. The page will reload with that store’s context.  
4. The choice is remembered for your session and can persist across reloads.

### Available stores

AGT Bothell • AGT Burien • AGT Goldbar • AGT Lynnwood • AGT Seattle • AGT Shoreline • AGT Walla Walla • Test

> **Important:** You cannot upload an Excel file until a store is selected. The file name should match the selected store (e.g., a file for Bothell should indicate “Bothell” in the name).

---

## 5. Main Workflow: Creating Labels

### Step-by-step workflow

| Step | Action |
|------|--------|
| 1 | Select store (if not already selected). |
| 2 | Load product data: upload Excel, use database only, or use **Match JSON** with a URL. |
| 3 | Refine the list using the filter dropdowns (Vendor, Brand, Product Type, Lineage, etc.). |
| 4 | Select tags in **Current Inventory** (left). Selected items appear in **Selected** (right). |
| 5 | Choose a **template** from the TEMPLATE dropdown. |
| 6 | Click **Generate Tags**. |
| 7 | Download the generated DOCX when the process completes. |

---

## 6. Uploading an Excel File

### 6.1 When to upload

- You have a store-specific Excel inventory file (e.g., from your POS or export).  
- You want labels to reflect that file’s products and data.

### 6.2 Procedure: Upload an Excel file

1. Ensure the correct **store** is selected.  
2. In the **filter bar** at the top, click **Upload Excel**.  
3. In the file picker, select an **.xlsx** or **.xls** file whose name matches the selected store.  
4. Wait for processing. The file name will appear near the upload button.  
5. When loading finishes, **Current Inventory** (left column) will list product tags. Use search and filters as needed.

### 6.3 Rules

- **Accepted formats:** Excel only (`.xlsx`, `.xls`).  
- **File name:** Must be valid for the selected store (validation runs on upload).  
- **Session:** One file per store per session; a new upload replaces the previous one.

### 6.4 Without an Excel file

- You can still use **Match JSON**; matching will use the product database when no Excel file is present.  
- You can also use **database-only** mode: no file upload, with the product list coming from the store’s product database.

---

## 7. Matching Products from a JSON URL

This feature matches products from an external **JSON URL** (e.g., Cultivera inventory transfer) to your Excel/database products and can add them to **Selected** in one step.

### 7.1 When to use it

- You have a JSON URL that lists products (e.g., a Cultivera inventory transfer URL).  
- You want to match those products to your Excel/database and add them to **Selected**.

### 7.2 Procedure: Match products from a JSON URL

1. (Recommended) Select a **store** and, if you use Excel, upload an Excel file first.  
2. In the filter bar, click **Match JSON**.  
3. In the **JSON Product Matching** modal:  
   - Paste the full JSON URL into the input (e.g. `https://...`).  
   - Click **Match JSON**.  
4. Wait for matching to complete (up to about two minutes for large data). Progress may appear in the modal or browser console.  
5. When finished:  
   - The modal shows how many products were matched and selected.  
   - Matched products are added to **Selected** (right column).  
   - **Current Inventory** may update with new tags from the match.  
6. Close the modal and continue with filters, template selection, and **Generate Tags** as needed.

### 7.3 URL requirements

- **Protocol:** HTTP or HTTPS (or `data:`). The app may add `https://` if omitted.  
- **Content:** The URL must return inventory transfer / product list JSON that the application can parse.

### 7.4 Detailed match view

Some flows offer a **detailed match** or “Before & After” view. You can review matches, use **Accept All Matches** or accept per item, then **Save** to apply the selection.

### 7.5 JSON Inventory Slips (separate feature)

**JSON Inventory Slips** (e.g., under Data Tools) is separate from **Match JSON**. There you paste a JSON URL to generate **inventory slip documents**, not to match and select tags for label generation.

---

## 8. Filtering and Selecting Tags

### 8.1 Screen layout

| Area | Content |
|------|---------|
| **Left** | **Current Inventory** — product tags from Excel and/or database (and from JSON match). |
| **Center** | Template selector, **Generate Tags** button, and controls (Undo, Redo, Clear, Export, Data & Analytics, Reset Cache, Lineage Editor). |
| **Right** | **Selected** — tags chosen for label generation. Items can be reordered by dragging. |

### 8.2 Filter dropdowns (top bar)

Use these to narrow **Current Inventory**:

- Vendor  
- Brand  
- Product Type  
- Lineage (e.g., Sativa, Indica, Hybrid)  
- Weight  
- Price  
- DOH Compliance  
- High CBD  

You can combine multiple filters.

### 8.3 Selecting tags

- **Manual:** In Current Inventory, check the products you want; they appear in **Selected**.  
- **Select All:** Use when available for a vendor/category to select a whole group.  
- **Search:** Use the search box above Current Inventory to find products by name or other text.  
- **Order:** Drag items in the **Selected** column to change order; order can affect layout in the generated document.

### 8.4 Clearing and resetting

- **Clear & Reset** (or “Clear Filters”): Clears selected tags and resets filters.  
- **Undo / Redo:** Reverses or re-applies the last selection change.

---

## 9. Generating and Downloading Labels

### 9.1 Before you generate

- At least one tag must be in **Selected** (right column).  
- Choose the **template** you want from the TEMPLATE dropdown.

### 9.2 Template options

| Template | Use |
|----------|-----|
| **Horizontal** | Horizontal label layout. |
| **Vertical** | Vertical label layout. |
| **Mini** | Smaller labels. |
| **Double** | Two-up or double layout. |
| **Preroll** | For pre-roll products. |
| **Inventory** | Inventory-style layout. |

### 9.3 Procedure: Generate labels

1. Set **TEMPLATE** to the desired layout.  
2. Click **Generate Tags**.  
3. Wait for generation (seconds to minutes depending on set size). A progress or status message may appear.  
4. When complete, the application will prompt or auto-download a **DOCX** file (e.g., “Labels.docx”). Save it to your computer.

### 9.4 After generation

- Use **Export Data** to download the **selected tags as Excel** (separate from the label DOCX).  
- To change layout, select a different **TEMPLATE** and click **Generate Tags** again.

---

## 10. Database and Data Tools

Tools are available from the center column or via **Data & Analytics**.

| Tool | Purpose |
|------|---------|
| **Export Data** | Download selected tags as an Excel file. |
| **Data & Analytics** | Open the product database manager: browse products, run analytics, **Edit DB** (add/edit/delete products). |
| **Reset Cache** | Clear cached data so the next load uses fresh data from Excel/database. Use when the list seems stale. |
| **Lineage Editor** | Manage strain names and lineage (e.g., Sativa/Indica/Hybrid) and related display. |

### 10.1 Database manager (Edit DB)

- View the product table, search, and run analytics.  
- **Edit** existing products (name, vendor, type, lineage, weight, price, DOH, etc.).  
- **Add** new products and **Delete** products you no longer need.  
- Changes affect Current Inventory and matching (including JSON match).

### 10.2 Backups and health

From the database/analytics UI you may **backup** the database, **restore** from backup, and check **database health**. Use these for safety and troubleshooting.

---

## 11. Troubleshooting

### 11.1 Store and upload

| Issue | Solution |
|-------|----------|
| “Please select a store before uploading” | Choose a store from the modal first, then upload. |
| Upload rejected (filename/store) | Ensure the Excel file name matches the selected store and the file is `.xlsx` or `.xls`. |

### 11.2 JSON match

| Issue | Solution |
|-------|----------|
| “Please enter a JSON URL first” | Paste a full URL in the JSON Match modal and click **Match JSON**. |
| Match fails or times out | Confirm the URL is reachable in a browser; allow 1–2 minutes for large payloads; ensure store is set and, if using Excel, that a file is uploaded. |

### 11.3 Tags and generation

| Issue | Solution |
|-------|----------|
| No tags in Current Inventory | Confirm store is selected; upload Excel or ensure the product database has products for that store; try **Reset Cache** and reload. |
| Generate does nothing or no download | Ensure at least one tag is in **Selected**; check browser download settings and pop-up blocker; check app logs or browser console (F12). |

### 11.4 Performance and cache

| Issue | Solution |
|------|----------|
| Slow or stale data | Use **Reset Cache** and reload; for heavy use, restart the application. |
| Port already in use | Use the URL shown in the console (app may use 8001–8010). Or set `FLASK_PORT` to a free port and restart. |

### 11.5 Network (other computers cannot connect)

- Use the **network URL** printed at startup (e.g. `http://<IP>:8001`).  
- Allow the application’s port in your firewall (Windows/macOS/Linux).  
- For local-only use, set `HOST=127.0.0.1` before starting; use port forwarding or a reverse proxy for remote access.

### 11.6 Logs

- **Server logs:** Log viewer (e.g. under **/logs** or linked from the UI).  
- **Browser:** Developer Tools (F12) → **Console** and **Network** for front-end and API errors.

---

## 12. Quick Reference

| Task | Action |
|------|--------|
| Start application | `python3 app.py` |
| Open application | Browser → `http://127.0.0.1:8001` (or URL shown in console) |
| Select store | Use modal on first load; required before upload |
| Load products | **Upload Excel** or **Match JSON** with a URL |
| Filter list | Use Vendor, Brand, Product Type, Lineage, etc. |
| Select for labels | Check items in Current Inventory; review Selected on the right |
| Generate labels | Choose **TEMPLATE** → **Generate Tags** → download DOCX |
| Export selection | **Export Data** (Excel of selected tags) |
| Manage products | **Data & Analytics** → Edit DB, backups, analytics |
| Fix stale data | **Reset Cache** and/or reload page |

---

## 13. Advanced: QR Codes, Preroll Template, and Product Data

### 13.1 QR codes on labels

- **What they are:** QR codes are printed on certain label templates (especially **Preroll**) to provide a detailed, always up-to-date view of products without overloading the physical tag.  
- **What they link to:**  
  - For **Preroll** labels, each QR code links to a **live product list page** (a preroll menu) for that vendor and group.  
  - The page shows product names, weights, THC/CBD information, and compliance details pulled from the same data that powers your tags.  
- **Vendor- and group-specific:** The QR URL is tied to a particular **preroll group and vendor**, so the page only shows the relevant products (not your entire inventory).  
- **Expiration behavior:** The preroll list behind a QR code is cached for a limited time (roughly a day). If it expires, the customer will see a message telling them to **scan a fresh QR code** from a newer label or menu.

> **Note:** THC/CBD percentages that used to be printed directly on some templates have been moved into the QR code flow. The label stays clean, while the QR page carries detailed test results when available.

### 13.2 Preroll template and preroll product list

- **Preroll template:**  
  - Designed specifically for **pre-roll joints and blunts**.  
  - Groups items into logical **preroll groups** (for example, by vendor, brand, strain, and pack size).  
  - Centers QR codes on the label so they are easy to scan in menus or on packaging.  
- **Preroll product list document:**  
  - When you generate tags with the **Preroll** template, the application also generates a **separate preroll product list DOCX** (a menu-style document) using the same groups.  
  - This list corresponds directly to the QR codes: scanning the QR on a tag opens the matching preroll group page.  
  - Use this menu alongside physical tags to give customers a full, readable listing of your prerolls.

> **Tip:** For best results, keep your **Product Type*** and **Description** fields in Excel accurate for prerolls (e.g., clearly indicating pre-roll, pack size, and weight). This helps the system group prerolls correctly and derive a useful **JointRatio** (see below).

### 13.3 Classic vs nonclassic product types

The application treats some product types as **classic** (traditional inhalable or cannabis-forward categories) and others as **nonclassic** (edibles, tinctures, topicals, etc.). This matters for **lineage colors**, **default lineage values**, and some analytics.

- **Classic types (examples):**  
  - Flower / Bud  
  - Pre-Roll / Preroll  
  - Concentrates (e.g., wax, shatter, rosin)  
  - Many standard Edibles
- **Nonclassic types (examples):**  
  - Tinctures, Oils, Capsules  
  - Topicals, Lotions, Balms  
  - Certain specialty edibles or non-THC-heavy formats

Key behaviors:

- **Classic types** can use the full set of lineages (Sativa, Indica, Hybrid, etc.).  
- **Nonclassic types** are normalized to high-level categories like **MIXED** or **CBD** instead of showing misleading Sativa/Indica labels.  
- The system automatically **enforces rules** so nonclassic products never show invalid classic-only lineages.

### 13.4 Lineages and strain handling

**Lineage** describes the overall Sativa/Indica/CBD character of a product and drives color-coding in many templates.

- **Typical lineage values:**  
  - `SATIVA`, `INDICA`, `HYBRID`  
  - `MIXED` (used heavily for nonclassic products and blended items)  
  - `CBD`, `CBD_BLEND` (for clearly CBD-forward or High CBD products)
- **Where lineage comes from:**  
  - Your Excel fields (`Lineage`, `Product Strain`, and strain-related columns).  
  - JSON product names and data (for JSON-matched products).  
  - The internal **strain database** when available (for example, filling in missing lineages or aligning vendor names with canonical strain data).
- **Safeguards:**  
  - If a classic product is tagged as `MIXED`, the system may normalize it to `HYBRID` to keep lineages consistent.  
  - Nonclassic products are forced into **MIXED** or **CBD** style categories; they will not show `SATIVA` or `INDICA` lineages on tags.

> **Practical impact:** The lineage you see on a tag is not always a direct copy of the Excel cell—it is often the **result of enrichment and validation** using JSON data, the strain database, and lineage rules designed to keep colors and wording consistent.

### 13.5 DOH compliance and High CBD products

Two important compliance-related concepts appear in filters and on tags: **DOH** and **High CBD**.

- **DOH (Department of Health) fields in Excel/database:**  
  - `DOH`  
  - `DOH Compliant (Yes/No)` (and similar variants)  
  - These are normalized internally so that the application can consistently tell whether a product is DOH-compliant, THC-only, CBD, etc.
- **High CBD products:**  
  - Identified primarily from the **Product Type** and DOH-style fields (for example, types beginning with “High CBD”).  
  - Always treated as **CBD-forward** products, which influences lineage (`CBD` / `CBD_BLEND`) and badge display.  

How this appears in the UI:

- The **High CBD** filter allows you to choose between **High CBD Products** and **Non-High CBD Products**.  
- On many templates, products can show **badges**:  
  - DOH badge: indicates DOH compliance for standard products.  
  - High CBD badge: indicates a High CBD product and often **replaces the DOH badge** (for High CBD items, CBD status takes priority).  
- For High CBD products, CBD/DOH logic is simplified so the High CBD status is always clear and not mixed with conflicting DOH labels.

### 13.6 Excel processing details (Description, JointRatio, and related fields)

The application does a significant amount of work behind the scenes when reading your Excel file. Some key fields:

- **`Product Name*`**: The primary identifier for products. Used for matching to the product database and JSON data.  
- **`Product Type*`**: Drives classic vs nonclassic logic, lineage behavior, High CBD detection, and which templates/products are eligible for preroll grouping.  
- **`Description`**:  
  - Used as human-readable text on many label templates.  
  - May be parsed to help detect preroll details (e.g., “infused preroll”, “shorty”, pack sizes).  
  - Keeping this concise and accurate improves grouping and reduces the chance of odd line breaks on labels.
- **`Lineage` / `Product Strain` / strain-related fields:**  
  - Provide initial lineage hints that are later enriched or corrected using the strain database and JSON data.  
  - Missing or inconsistent values can often be corrected automatically, but cleaner input leads to more predictable tag colors and wording.
- **`Weight*` and `Weight Unit* (grams/gm or ounces/oz)`**:  
  - Used to compute display weights and to help infer pack sizes for prerolls.  
  - Also used as a fallback when other information (like JointRatio) is missing.
- **`DOH` and `DOH Compliant (Yes/No)`**:  
  - Normalized into a single internal DOH value.  
  - Control DOH badge display and can influence how CBD vs. THC status is interpreted.

#### JointRatio for prerolls

**JointRatio** is a derived value used primarily for preroll menus and grouping. It describes **how many grams per joint and how many joints per pack**.

- **If your Excel already has `JointRatio` or `Joint Ratio`:**  
  - Those values are used directly when they are valid (non-empty and non-zero).  
  - Example formats: `0.5g x 2`, `1g x 5`.
- **If `JointRatio` is missing:** the system tries to infer it in several stages:  
  1. **Look up** a matching product in the product database and reuse its `JointRatio`.  
  2. **Parse the product name** for patterns like `0.5g x 2 Pack`, `1g x 5`, or `5pk` and calculate a `weight g x count` ratio.  
  3. **Fallback to weight:** if nothing else is available, build a ratio-like string from `Weight*` and its units (e.g., `1g`, `3.5g`, or `1oz`).
- **Why this matters:**  
  - The `JointRatio` is used for preroll grouping and presentation in preroll menus and QR-backed pages.  
  - Providing a clear pack format in **Product Name*** and/or a valid `JointRatio` column makes preroll menus far more readable.

> **Recommendation:** When you define new preroll products in Excel, include either a clean **JointRatio** (such as `0.5g x 2`) or a product name that clearly encodes weight and pack size. This lets the application calculate sensible preroll groupings and QR-backed menus with minimal manual cleanup.

---

## Related documentation

- **Installation details:** `INSTALLATION.md`  
- **Performance and API:** `QUICK_START_GUIDE.md`, `api_endpoints_summary.md`

---

*AGT Designer — User Manual v1.1*
