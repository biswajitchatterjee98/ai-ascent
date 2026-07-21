# AI Ascent

**AI Ascent**: rich, practical AI learning guide (27 topics) with a side-panel reader and program registration.

| File | Use |
|------|-----|
| `TOPIC-OUTLINE.md` | Topic/subtopic analysis |
| `AI-Ascent.md` | Full source content |
| `index.html` | Interactive handbook (open in a browser) |
| `login.html` | Redirect stub (login lives on traininglobe-hub) |
| `admin.html` | Access admin (restrict sections, approve requests, grants) |
| `content-manifest.json` | Stable section IDs for access control |
| `config.js` / `api.js` / `auth.js` / `access.js` | Auth + section gating clients |
| `register.html` | AI Practitioner program registration form |
| `google-apps-script/` | Sheet-backed access API (deploy guide inside) |
| `images/` | Topic photos + YouTube thumbnails |
| `scripts/build_html.py` | Rebuild `index.html` + `content-manifest.json` |
| `scripts/download_assets.py` | Refresh image / thumbnail assets |

## Open locally

```bash
open index.html
```

Or serve the folder:

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

## Rebuild after editing Markdown

```bash
python3 scripts/build_html.py
```

## Registration

Open **`register.html`** (sidebar: Register · Practitioner Program). Submissions go to `atharv.kumar@webisdom.com` via FormSubmit.

## Access

Handbook pages open without a local login. Sign in on the Traininglobe hub; opening AI Ascent from there passes a short-lived `hub_token` so the sidebar can show who you are. Direct bookmarks to `index.html` still work.

`login.html` only redirects to the handbook (for old links).

## Access control

Same model as the AI Tools Playbook:

1. Deploy `google-apps-script/Code.gs` (see that folder’s README).
2. Set `API_URL` in `config.js` to the Web App `/exec` URL.
3. Sign in as `admin` / `Admin@123`, open **Admin** in the sidebar.
4. Restrict any topic or subsection, grant access manually, or approve **Get access** requests with optional expiry.

Until `API_URL` is set, all sections stay visible (gates need the API). Admin access still uses the local admin account when configured.
