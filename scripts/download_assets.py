#!/usr/bin/env python3
"""Download topic images (Unsplash) and YouTube thumbnails."""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "images" / "topics"
YT = ROOT / "images" / "youtube"
MD = ROOT / "AI-Practitioner-Handbook.md"
PLAYBOOK = ROOT.parent / "ai-tools-playbook" / "images"

# Curated Unsplash photo IDs (w=1200 crop)
UNSPLASH = {
 "industries.jpg": "1504384308090-c894fdcc538d",
 "intelligent-ladder.jpg": "1434626881859-194d67b2b86f",
 "intelligent-hierarchy.jpg": "1454165804606-c3d57bc86b40",
 "ai-ml-dl.jpg": "1518770660439-4636190af475",
 "ani-agi-asi.jpg": "1446776811953-b23d57bd21aa",
 "text-generation.jpg": "1455390582262-044cdead277a",
 "neural-networks.jpg": "1558494949-ef010cbdcc31",
 "transformers.jpg": "1620712943543-bcc4688e7485",
 "stable-diffusion.jpg": "1547036967-23d11aacaee0",
 "image-learning.jpg": "1541963463532-d68292c34b19",
 "email-generation.jpg": "1557207284-6ae1e4ed7cee",
 "report-generation.jpg": "1551288049-bebda4e38f71",
 "presentations.jpg": "1557804506-669a67965ba0",
 "deepfake.jpg": "1526374965328-7f61d4dc18c5",
 "cybersecurity.jpg": "1550751827-4bd374c3f58b",
 "ethics-governance.jpg": "1589820298136-8f3f9e3b3d0e", # may 404: fallback below
 "functional-ai.jpg": "1522071820081-009f0129c71c",
 "ai-strategy.jpg": "1454165804606-c3d57bc86b40",
 "chatgpt.jpg": "1677442136019-21780ecad995",
 "gemini.jpg": "1486312338219-ce68d2c6f44d",
 "claude.jpg": "1456513080830-a4f7d77da439",
 "llm-choice.jpg": "1507679799987-c73779587ccf",
 "automate-tasks.jpg": "1518186285589-2f7649de83e0",
 "makecom.jpg": "1558494949-ef010cbdcc31",
 "n8n-agents.jpg": "1485827404703-89b55fcc595e",
 "wrap-up.jpg": "1522202176988-66273c2fd55f",
 "practitioner-program.jpg": "1523240795612-9a054b0db644",
}

# Safer known Unsplash IDs if primary fails
FALLBACK = "1518770660439-4636190af475"

# Reuse playbook locals when filenames match themes
PLAYBOOK_COPY = {
 "chatgpt.jpg": "topics/chatgpt.jpg",
 "claude.jpg": "topics/claude.jpg",
 "email-generation.jpg": "topics/email.jpg",
 "makecom.jpg": "topics/make.jpg",
 "presentations.jpg": "topics/gamma.jpg",
 "gemini.jpg": "topics/workspace.jpg",
}


def fetch(url: str, dest: Path) -> bool:
 try:
 req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
 with urllib.request.urlopen(req, timeout=40) as r:
 data = r.read()
 if len(data) < 2000:
 return False
 dest.write_bytes(data)
 print(f"OK {dest.name} ({len(data)} bytes)")
 return True
 except Exception as e:
 print(f"FAIL {dest.name}: {e}")
 return False


def main() -> None:
 TOPICS.mkdir(parents=True, exist_ok=True)
 YT.mkdir(parents=True, exist_ok=True)

 # Topic images from MD
 slugs = sorted(set(re.findall(r"images/topics/([a-z0-9-]+\.jpg)", MD.read_text())))
 for slug in slugs:
 dest = TOPICS / slug
 if dest.exists() and dest.stat().st_size > 5000:
 print(f"skip {slug}")
 continue
 # playbook reuse
 rel = PLAYBOOK_COPY.get(slug)
 if rel:
 src = PLAYBOOK / rel
 if src.exists():
 dest.write_bytes(src.read_bytes())
 print(f"copy {slug} from playbook")
 continue
 photo = UNSPLASH.get(slug, FALLBACK)
 url = f"https://images.unsplash.com/photo-{photo}?auto=format&fit=crop&w=1200&h=675&q=80"
 if not fetch(url, dest):
 url2 = f"https://images.unsplash.com/photo-{FALLBACK}?auto=format&fit=crop&w=1200&h=675&q=80"
 fetch(url2, dest)

 # YouTube thumbs
 ids = sorted(set(re.findall(r"youtube\.com/watch\?v=([A-Za-z0-9_-]+)", MD.read_text())))
 for vid in ids:
 dest = YT / f"{vid}.jpg"
 if dest.exists() and dest.stat().st_size > 1000:
 print(f"skip yt {vid}")
 continue
 # try maxres then hq
 ok = fetch(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", dest)
 if not ok:
 fetch(f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg", dest)

 print(f"Done. topics={len(list(TOPICS.glob('*.jpg')))} youtube={len(list(YT.glob('*.jpg')))}")


if __name__ == "__main__":
 main()
