# POSaBit API Integration

The Label Maker can use **POSaBit's API** instead of Excel for product lists and manifests.

## Overview

- **Products (menu)**: When enabled, the app loads the product list from POSaBit's Menu Feed API instead of an uploaded or default Excel file.
- **Manifests**: You can load manifest items from POSaBit and generate inventory slips without pasting a JSON URL.

## Requirements

- Active **POSaBit venue API token** (and, for products, a **menu feed key**) from your POSaBit account.
- API docs: [POSaBIT POS API](https://developer.posabit.com/pos.html).

## Environment Variables

Set these in your environment (e.g. `.env` or server config). **Do not commit secrets.**

| Variable | Required | Description |
|----------|----------|-------------|
| `POSABIT_API_TOKEN` | Yes* | Your POSaBit API (Bearer) token. |
| `POSABIT_ORDER_PAD_TOKEN` | No | Order Pad integration token (from Settings > Integrations in app.posabit.com). When set, used for menu feed and venue inventories instead of `POSABIT_API_TOKEN`. |
| `POSABIT_API_BASE_URL` | No | Base URL. Default: `https://app.posabit.com/api`. Use `https://staging-app.posabit.com/api` for staging. |
| `POSABIT_MENU_FEED_KEY` | For products (menu feed) | Menu feed UUID. Omit if using venue inventories only. |
| `POSABIT_USE_VENUE_INVENTORIES` | No | Set to `1`, `true`, or `yes` to load products from **GET /v2/venue/inventories** first (full inventory; recommended for label maker). |
| `POSABIT_PREFER_MENU_FEED` | No | Set to `1`/`true` to keep menu-feed-only behavior (typically ~100–200 menu-listed items). |
| `POSABIT_VENUE_INVENTORY_FALLBACK_THRESHOLD` | No | When menu feed returns fewer than this many rows (default `250`), auto-fetch venue inventories if larger. |
| `POSABIT_MAX_PRODUCTS` | No | Max venue inventory rows to load (default `10000`; set `0` for no cap). |
| `POSABIT_VENUE_INVENTORY_INCLUDE_INACTIVE` | No | When using venue inventories: set to `1`/`true` to include inactive SKUs. Default: active only. |
| `POSABIT_VENUE_INVENTORY_INCLUDE_ZERO_QUANTITY` | No | When using venue inventories: set to `1`/`true` to include SKUs with zero quantity on hand. Default: in-stock only (`q[quantity_on_hand_gt]=0`). Unfiltered inventory is 30k+ historical SKUs and will time out. |
| `USE_POSABIT_PRODUCTS` | No | Set to `1`, `true`, or `yes` to use POSaBit as the product source instead of Excel. |
| `USE_POSABIT_MANIFESTS` | No | Set to `1`, `true`, or `yes` to allow loading manifests from POSaBit in the UI. |

## Using POSaBit for Products (Replace Excel)

1. In **app.posabit.com**, create a menu feed (or use an existing one) and set its **Product List** to **Active** so the feed includes your active products. Copy the **menu feed key**.
2. Get your **API token** (same as used for menu/orders).
3. Set in your environment:
   - `POSABIT_API_TOKEN=<your-token>`
   - `POSABIT_MENU_FEED_KEY=<menu-feed-uuid>`
   - `USE_POSABIT_PRODUCTS=true`
4. Restart the app. On load (when no Excel file is in session), the app will fetch the menu feed and use it as the product list for tags and matching.

## Using POSaBit for Manifests

1. Set `POSABIT_API_TOKEN` and optionally `POSABIT_API_BASE_URL`.
2. In the app, open **JSON Inventory Slips** (modal or menu that generates inventory slips from JSON).
3. Click **Load manifest from POSaBit**. The app will call the POSaBit venue API, fetch manifests, and generate the inventory slip DOCX from that data.

No need to set `USE_POSABIT_MANIFESTS` for the button to appear; the button is always shown. If the token is not set, the request will fail with a clear error.

## API Endpoints Used

- **Menu feed (products)**: `GET https://app.posabit.com/api/v1/menu_feeds/{feed_key}` with `Authorization: Bearer <token>`.
- **Venue inventories (products, alternative)**: `GET {base_url}/v2/venue/inventories` with `Authorization: Bearer <token>`. No feed key required; use when menu feed returns 0 products or set `POSABIT_USE_VENUE_INVENTORIES=1`.
- **Manifests**: `GET {base_url}/v2/venue/manifests` with `Authorization: Bearer <token>`.

## Status API

- `GET /api/posabit/config` — Returns (no secrets): `use_products`, `use_manifests`, `has_token`, `has_feed_key`, `base_url`. Use this in the UI to show integration status.

---

## Safe deployment on a public web server

Never put your POSaBit token or feed key in code or in a file that is committed to git. Use **environment variables** set by your hosting provider so secrets stay in the server’s config, not in the repo or on disk where they could be read.

### Rules

1. **Do not** commit `.env`, `secrets.py`, or any file containing `POSABIT_API_TOKEN` or `POSABIT_MENU_FEED_KEY`. (`.env` is already in `.gitignore`.)
2. **Do not** paste the token into `wsgi.py`, `app.py`, or any file in the repo.
3. **Do** set the variables in your host’s “Environment variables” (or equivalent) so only the running app can see them.
4. **Do** use **HTTPS** so the token is never sent in the clear.

### PythonAnywhere

1. Open the **Web** tab for your app.
2. Scroll to **“Environment variables”** (or “Code” → “Environment variables”).
3. Add each variable (name + value). For example:
   - `POSABIT_API_TOKEN` = `your_actual_token`
   - `POSABIT_MENU_FEED_KEY` = `8965dc69-d3aa-439c-877d-c5c407b0f1dc`
   - `POSABIT_API_BASE_URL` = `https://app.posabit.com/api`
   - `USE_POSABIT_PRODUCTS` = `true`
4. Save, then **reload** your web app (green “Reload” button).  
   The app will read these at startup; they are not stored in your project files.

Your token and feed key never go into the codebase or into a file under your project directory.

### Other hosts (Heroku, Railway, Render, VPS, etc.)

- **Heroku**: Settings → Config Vars → Add each variable.
- **Railway / Render**: Project → Variables (or Environment) → add the same names and values.
- **VPS (Linux)** (e.g. systemd or gunicorn):
  - Prefer your process manager’s env config (e.g. `Environment=POSABIT_API_TOKEN=...` in a systemd unit, or a small env file **outside** the web root with permissions `chmod 600` and owned by the app user).
  - Do **not** put the token in a file inside the public web directory or in any file that gets committed.

### If you use a `.env` file on the server

Only do this if your host doesn’t provide env vars and you must use a file:

- Create `.env` **outside** the directory that is served as static/web root (e.g. one level above, or in the app user’s home).
- Run: `chmod 600 .env` and ensure the file is owned by the user that runs the app.
- Load it at startup (e.g. with `python-dotenv` in `app.py` **before** creating the app) and **never** commit `.env` or serve it.

### What the app exposes

- The token is only used in server-side requests to POSaBit; it is **never** sent to the browser or logged.
- `GET /api/posabit/config` returns only whether a token/feed key is **set** (`has_token`, `has_feed_key`), not their values.
