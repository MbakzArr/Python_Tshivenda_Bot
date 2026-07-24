import json
import os
import random
import time

from core import paths

CACHE_FILE = paths.user("news_cache.json")
CACHE_MINUTES = 30
TIMEOUT = 10

SOURCES = [
    ("Limpopo Mirror", "https://www.limpopomirror.co.za/articles/venda"),
    ("Limpopo Mirror News", "https://www.limpopomirror.co.za/articles/news"),
]


def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (ValueError, OSError):
        return None
    if time.time() - raw.get("fetched", 0) > CACHE_MINUTES * 60:
        return raw if raw.get("articles") else None
    return raw


def _save_cache(articles):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"fetched": time.time(), "articles": articles}, f,
                      ensure_ascii=False, indent=2)
    except OSError:
        pass


def scrape(url, source):
    """Pull articles off one page. Returns a list, never raises."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    try:
        resp = requests.get(url, timeout=TIMEOUT,
                            headers={"User-Agent": "TshivendaBot/2.0"})
    except Exception:
        return []

    if resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for block in soup.find_all("div", class_="art"):
        try:
            h = block.find("h3")
            title = h.get_text(strip=True) if h else ""
            if not title:
                continue
            d = block.find("span", class_="date")
            syn = block.find("div", class_="syn")
            body = ""
            if syn:
                p = syn.find("p")
                body = p.get_text(strip=True) if p else syn.get_text(strip=True)
            link = ""
            a = block.find("a", href=True)
            if a:
                link = a["href"]
                if link.startswith("/"):
                    link = "https://www.limpopomirror.co.za" + link
            out.append({
                "title": title,
                "date": d.get_text(strip=True) if d else "Unknown",
                "summary": body,
                "link": link,
                "source": source,
            })
        except Exception:
            continue
    return out


def fetch(force=False):
    """All articles, from cache when it is fresh."""
    if not force:
        cached = _load_cache()
        if cached and time.time() - cached.get("fetched", 0) <= CACHE_MINUTES * 60:
            return cached["articles"], True

    articles = []
    for source, url in SOURCES:
        articles.extend(scrape(url, source))
        if articles:
            break

    if articles:
        _save_cache(articles)
        return articles, False

    stale = _load_cache()
    if stale and stale.get("articles"):
        return stale["articles"], True
    return [], False


def headlines(limit=5):
    articles, cached = fetch()
    if not articles:
        return "Could not reach the news site and there is nothing cached. Check your connection."
    lines = ["Latest headlines%s:" % (" (cached)" if cached else "")]
    for n, a in enumerate(articles[:limit], 1):
        lines.append("  %d. %s  [%s]" % (n, a["title"], a["date"]))
    lines.append("Use /news to read a random one in full.")
    return "\n".join(lines)


def random_article():
    articles, cached = fetch()
    if not articles:
        return "Could not reach the news site and there is nothing cached. Check your connection."
    a = random.choice(articles)
    lines = [
        "Source: %s%s" % (a["source"], " (cached)" if cached else ""),
        "Date:   %s" % a["date"],
        "Title:  %s" % a["title"],
        "",
        a["summary"] or "(no summary available)",
    ]
    if a.get("link"):
        lines.append("")
        lines.append("Read more: %s" % a["link"])
    return "\n".join(lines)
