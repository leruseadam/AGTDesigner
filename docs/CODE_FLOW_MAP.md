# AGT Designer — Code Flow Map

A simple map of how the main features flow through the codebase.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BROWSER (templates/index.html + static/js/main.js)                          │
│  TagManager state, filters, selected tags, cache hydration                   │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  app.py (Flask)                                                              │
│  Routes: /upload, /api/json-match, /api/available-tags, /api/generate, etc. │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────────┐
│ excel_processor│         │ json_matcher /  │         │ template_processor  │
│ (Excel load,  │         │ enhanced_json_  │         │ (label context,      │
│  tags, filter)│         │ matcher (match)  │         │  DOCX generation)   │
└───────┬───────┘         └────────┬────────┘         └──────────┬──────────┘
        │                          │                             │
        └──────────────────────────┼─────────────────────────────┘
                                   ▼
                        ┌─────────────────────┐
                        │ product_database     │
                        │ (SQLite/PostgreSQL) │
                        │ Vendor, Price,      │
                        │ Lineage, DOH        │
                        └─────────────────────┘
```

---

## Main User Flows

### 1. Upload Excel → See inventory

| Step | Where | What happens |
|------|--------|----------------|
| 1 | UI | User clicks "Upload Excel", picks file |
| 2 | `POST /upload` or `POST /upload-lightning` | app.py receives file |
| 3 | app.py | Saves file, calls `get_session_excel_processor()`, loads into pandas DataFrame |
| 4 | excel_processor | Processes rows → tags; `_enrich_tags_with_database_values(tags)` fills Vendor/Price/Lineage from DB |
| 5 | app.py | Caches tags, returns success |
| 6 | UI | Calls `GET /api/available-tags` → tags displayed in "CURRENT INVENTORY" |

**Key files:** `app.py` (upload routes, ~3390, 5826), `src/core/data/excel_processor.py` (load, enrich, get_available_tags)

---

### 2. Match JSON → See matched tags

| Step | Where | What happens |
|------|--------|----------------|
| 1 | UI | User enters JSON URL, clicks "Match JSON" |
| 2 | `POST /api/json-match` | app.py, body: `{ "url": "..." }` |
| 3 | app.py | `get_session_json_matcher()` → EnhancedJSONMatcher or JSONMatcher |
| 4 | json_matcher | `fetch_and_match_with_product_db(url, force_simplified=True)` → fast match, no DB in matcher |
| 5 | app.py | `excel_processor._enrich_tags_with_database_values(matched_products)` → DB used here |
| 6 | app.py | Normalize names, dedupe, clean weight/price; store in cache; return `available_tags` + `selected_tags` |
| 7 | UI | TagManager updates available + selected from response |

**Key files:** `app.py` (json_match ~20866, enrichment after 20995), `src/core/data/json_matcher.py` (fetch_and_match, fetch_and_match_with_product_db), `src/core/data/excel_processor.py` (_enrich_tags_with_database_values)

---

### 3. Get available tags (list / filters)

| Step | Where | What happens |
|------|--------|----------------|
| 1 | UI | Page load or refresh; TagManager may hydrate from localStorage cache first |
| 2 | `GET /api/available-tags` | app.py `get_available_tags()` |
| 3 | app.py | `get_session_excel_processor()` → `excel_processor.get_available_tags(filters)` or cache |
| 4 | excel_processor | Filter by vendor/type/lineage/weight/price; optional DB enrichment on cached tags |
| 5 | app.py | Return `{ tags, total_count, source }` |
| 6 | UI | TagManager._updateAvailableTags(tags); builds vendor/type/weight groups for left panel |

**Key files:** `app.py` (get_available_tags ~11996), `src/core/data/excel_processor.py` (get_available_tags, filter + cache)

---

### 4. Generate labels (DOCX)

| Step | Where | What happens |
|------|--------|----------------|
| 1 | UI | User selects tags, picks template (e.g. Horizontal), clicks "Generate Tags" |
| 2 | `POST /api/generate` | app.py, body: `selected_tags`, `template_type`, `template_group`, `scale_factor` |
| 3 | app.py | Build `records` from selected_tags (and/or excel_processor by selection); restore full DataFrame early to avoid race with /api/available-tags |
| 4 | template_processor | For each record, `_build_label_context(record, ...)` → ProductName, DescAndWeight, Price, Lineage, JointRatio, etc. |
| 5 | app.py + docx | Fill Word template (classic or user), apply font sizing; build final .docx |
| 6 | app.py | Return docx file download |

**Key files:** `app.py` (generate_labels ~9275, record building, docx assembly), `src/core/generation/template_processor.py` (_build_label_context, DescAndWeight, placeholders), `src/core/generation/` (docx fill, unified_font_sizing)

---

## Flow Diagram (Mermaid)

```mermaid
flowchart LR
    subgraph UI
        A[Upload Excel] --> B[Match JSON]
        B --> C[Select tags]
        C --> D[Generate Tags]
    end

    subgraph Backend
        A --> E[/upload]
        B --> F[/api/json-match]
        C --> G[/api/available-tags]
        D --> H[/api/generate]
    end

    subgraph Data
        E --> I[excel_processor]
        F --> J[json_matcher]
        F --> K[_enrich_tags_with_database_values]
        G --> I
        H --> L[template_processor]
        I --> M[product_database]
        K --> M
        L --> M
    end
```

---

## Important Paths in app.py

| Route | Approx. line | Purpose |
|-------|----------------|--------|
| `GET /` | 3170 | Serve main UI (index.html) |
| `POST /upload` | 3390 | Classic Excel upload |
| `POST /upload-lightning` | 5826 | Fast Excel upload |
| `POST /api/json-match` | 20866 | Match JSON URL → tags + DB enrichment |
| `GET /api/available-tags` | 11996 | Return tag list (with filters/cache) |
| `POST /api/selected-tags` | 15405 | Update selected tags (if used) |
| `POST /api/generate` | 9275 | Build records, run template_processor, return DOCX |

---

## Where DB data is used

- **Excel tags:** `excel_processor.get_available_tags()` → internally calls `_enrich_tags_with_database_values(tags)` so Vendor, Price, Lineage come from `product_database` when missing.
- **JSON-matched tags:** After `fetch_and_match_with_product_db(..., force_simplified=True)`, app.py calls `excel_processor._enrich_tags_with_database_values(matched_products)` so DB is used for JSON match too.
- **Label generation:** `template_processor._build_label_context(record, ...)` reads record fields (many of which were filled from DB during enrichment) and builds DescAndWeight, Price, Lineage, etc. for the DOCX.

---

*This map is a simplified view; exact line numbers may shift with edits.*
