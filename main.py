import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ================== CONFIG (ENV) ==================
START_URL       = os.getenv("START_URL", "http://localhost").strip()
CANONICAL_BASE  = os.getenv("CANONICAL_BASE", "https://www.example.com").strip()
OUTPUT_PATH     = os.getenv("OUTPUT_PATH", "./sitemap.xml").strip()

MAX_PAGES       = int(os.getenv("MAX_PAGES", "1000"))
REQ_TIMEOUT     = int(os.getenv("REQ_TIMEOUT", "10"))
CRAWL_DELAY_SEC = float(os.getenv("CRAWL_DELAY_SEC", "0.2"))

EXCLUDE_PREFIXES = tuple(
    p.strip() for p in os.getenv("EXCLUDE_PREFIXES", "/admin,/login,/panel").split(",") if p.strip()
)

CRAWLER_UA = os.getenv("CRAWLER_UA", "SimpleCrawler/1.0")
ALLOWED_SCHEMES = ("http", "https")

CHANGEFREQ = os.getenv("CHANGEFREQ", "weekly")
PRIORITY   = os.getenv("PRIORITY", "0.5")
# ===================================================

session = requests.Session()
session.headers.update({"User-Agent": CRAWLER_UA})

def same_host(u: str, base: str) -> bool:
    return urlparse(u).netloc == urlparse(base).netloc

def normalize(u: str) -> str:
    p = urlparse(u)
    if p.scheme not in ALLOWED_SCHEMES:
        return ""
    p = p._replace(query="", fragment="")
    norm = urlunparse(p)
    if norm.endswith("//"):
        norm = norm[:-1]
    return norm

def to_canonical(u: str) -> str:
    p = urlparse(u)
    base = urlparse(CANONICAL_BASE)
    return urlunparse((base.scheme, base.netloc, p.path or "/", "", "", ""))

def should_include(path: str) -> bool:
    return not any(path.startswith(pref) for pref in EXCLUDE_PREFIXES)

def detect_lastmod(url: str) -> str:
    try:
        r = session.head(url, timeout=REQ_TIMEOUT, allow_redirects=True)
        hdr = r.headers.get("Last-Modified")
        if hdr:
            try:
                dt = datetime.strptime(hdr, "%a, %d %b %Y %H:%M:%S %Z")
                return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            except Exception:
                pass
    except requests.RequestException:
        pass
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")

def crawl(start_url: str) -> list[str]:
    visited: set[str] = set()
    found: set[str] = set()
    q = deque([start_url])
    start_host = urlparse(start_url).netloc

    while q and len(found) < MAX_PAGES:
        current = normalize(q.popleft())
        if not current or current in visited or not same_host(current, start_url):
            continue
        visited.add(current)

        try:
            r = session.get(current, timeout=REQ_TIMEOUT, allow_redirects=True)
            print(f"[{r.status_code}] {current} -> {r.url}")
            if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            can_url = to_canonical(current)
            if should_include(urlparse(can_url).path):
                found.add(can_url)

            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href or href.startswith(("mailto:", "tel:", "javascript:")):
                    continue
                nxt = urljoin(r.url, href)
                nxt = normalize(nxt)
                if not nxt:
                    continue
                if not same_host(nxt, start_url):
                    continue
                if not should_include(urlparse(nxt).path):
                    continue
                if nxt not in visited:
                    q.append(nxt)

            time.sleep(CRAWL_DELAY_SEC)

        except requests.RequestException as e:
            print(f"[ERR] {current} -> {e}")

    return sorted(found)

def generate_sitemap(urls: list[str]) -> str:
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lastmod = detect_lastmod(u)
        parts += [
            "  <url>",
            f"    <loc>{u}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            f"    <changefreq>{CHANGEFREQ}</changefreq>",
            f"    <priority>{PRIORITY}</priority>",
            "  </url>"
        ]
    parts.append("</urlset>")
    return "\n".join(parts)

if __name__ == "__main__":
    urls = crawl(START_URL)
    print(f"Toplam URL: {len(urls)}")
    xml = generate_sitemap(urls)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"sitemap.xml yazıldı -> {OUTPUT_PATH}")
