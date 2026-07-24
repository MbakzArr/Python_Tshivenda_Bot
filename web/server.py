"""Web interface. Standard library only, no Flask, no Django.

    python bot.py --web
    python bot.py --web --port 8080 --open

Runs entirely on your own machine. Nothing is sent anywhere.
"""

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.api import Service

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "application/javascript; charset=utf-8", ".json": "application/json",
         ".svg": "image/svg+xml", ".ico": "image/x-icon"}

service = Service()
lock = threading.Lock()


def routes(path, query, body):
    """Return a dict for the given API path, or None if the path is unknown."""
    q = lambda k, d="": (query.get(k, [d])[0] or d).strip()

    if path == "/api/stats":
        return service.stats()

    if path == "/api/categories":
        return {"categories": service.categories()}

    if path == "/api/translate":
        text = body.get("text") or q("text")
        if not text:
            return {"ok": False, "error": "Nothing to translate."}
        return service.translate(text, body.get("direction") or q("direction") or None)

    if path == "/api/define":
        return service.define(body.get("word") or q("word"))

    if path == "/api/search":
        return {"results": service.search(body.get("q") or q("q"))}

    if path == "/api/word":
        return {"entry": service.word_of_day()}

    if path == "/api/quiz":
        return service.new_question(category=body.get("category") or q("category"))

    if path == "/api/answer":
        return service.answer(body.get("token", ""), body.get("given", ""))

    if path == "/api/drill":
        return {"queue": service.drill_queue(int(body.get("size") or q("size", "10")))}

    if path == "/api/drill/question":
        return service.question_for(body.get("id") or q("id"))

    if path == "/api/riddle":
        return {"item": service.riddle()}

    if path == "/api/proverb":
        return {"item": service.proverb()}

    if path == "/api/joke":
        return {"item": service.joke()}

    if path == "/api/culture":
        topic = body.get("topic") or q("topic")
        return {"item": service.culture(topic), "topics": service.culture_topics()}

    if path == "/api/news":
        return service.news()

    if path == "/api/add":
        return service.add_word(body.get("en", ""), body.get("ve", ""),
                                body.get("category", "general"),
                                body.get("pos", ""), body.get("note", ""))

    if path == "/api/add-content":
        return service.add_content(body.get("kind", ""), body.get("item", {}))

    if path == "/api/pending":
        return service.pending(int(body.get("limit") or q("limit", "25")))

    if path == "/api/review":
        return service.review(body.get("id", ""), body.get("action", ""),
                              body.get("ve", ""))
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "TshivendaBot/2.0"

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet

    def _send(self, code, payload, ctype="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _static(self, path):
        name = "index.html" if path in ("/", "") else path.lstrip("/")
        target = os.path.abspath(os.path.join(STATIC, name))
        if not target.startswith(os.path.abspath(STATIC)) or not os.path.isfile(target):
            return self._send(404, {"error": "Not found"})
        ext = os.path.splitext(target)[1]
        with open(target, "rb") as f:
            self._send(200, f.read(), TYPES.get(ext, "application/octet-stream"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            return self._static(parsed.path)
        try:
            with lock:
                out = routes(parsed.path, parse_qs(parsed.query), {})
        except Exception as err:
            return self._send(500, {"ok": False, "error": str(err)})
        if out is None:
            return self._send(404, {"ok": False, "error": "Unknown endpoint."})
        self._send(200, out)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except ValueError:
            return self._send(400, {"ok": False, "error": "Body was not valid JSON."})
        try:
            with lock:
                out = routes(parsed.path, parse_qs(parsed.query), body)
        except Exception as err:
            return self._send(500, {"ok": False, "error": str(err)})
        if out is None:
            return self._send(404, {"ok": False, "error": "Unknown endpoint."})
        self._send(200, out)


def serve(port=8000, open_browser=False, host="127.0.0.1"):
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = "http://%s:%d" % ("localhost" if host == "127.0.0.1" else host, port)
    print("Tshivenda Bot is running at %s" % url)
    print("%d dictionary entries loaded. Press Ctrl+C to stop." % len(service.lex.entries))
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
