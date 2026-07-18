# AI Ascent

**AI Ascent**: rich, practical AI learning guide (27 topics) with a side-panel reader and program registration.

| File | Use |
|------|-----|
| `TOPIC-OUTLINE.md` | Topic/subtopic analysis |
| `AI-Ascent.md` | Full source content |
| `index.html` | Interactive handbook (open in a browser) |
| `login.html` | Sign-in gate (required before handbook access) |
| `auth.js` | Demo usernames/passwords + session helpers |
| `register.html` | AI Practitioner program registration form |
| `images/` | Topic photos + YouTube thumbnails |
| `scripts/build_html.py` | Rebuild `index.html` from the Markdown |
| `scripts/download_assets.py` | Refresh image / thumbnail assets |

## Open locally

```bash
open index.html
```

Or serve the folder:

```bash
python3 -m http.server 8080
# then visit http://localhost: 8080
```

## Rebuild after editing Markdown

```bash
python3 scripts/build_html.py
```

## Registration

Open **`register.html`** (sidebar: Register · Practitioner Program). Submissions go to `atharv.kumar@webisdom.com` via FormSubmit.


## Login

Open `login.html` first. Use the username and password issued to you. Session lasts until logout or the tab is closed.
