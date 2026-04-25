"""Minimal FastAPI app used by the swarm-bots fleet as a live test bed.

Endpoints
---------
  GET /                 landing page (HTML)
  GET /fortune          random fortune
  GET /fortune/{id}     specific fortune (triggers Logan when `id` is invalid)
  GET /crash            intentional 500 (keeps Logan busy with a repeat pattern)
  GET /health           liveness probe
"""

from __future__ import annotations

import random

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app import logger
from app.fortunes import all_fortunes, fortune_by_id

app = FastAPI(title="swarm-lab")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    f = random.choice(all_fortunes())
    return f"""
    <!doctype html>
    <html><head><title>swarm-lab</title>
      <style>body{{font:16px system-ui;max-width:38rem;margin:3rem auto;padding:0 1rem;color:#222}}
      blockquote{{border-left:3px solid #ddd;padding-left:1rem;color:#555}}</style></head>
    <body>
      <h1>swarm-lab</h1>
      <blockquote>{f.text}<footer>— {f.author or 'unknown'}</footer></blockquote>
      <p><a href="/fortune">/fortune</a> · <a href="/fortune/{f.id}">/fortune/{f.id}</a> · <a href="/health">/health</a></p>
    </body></html>
    """


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/fortune")
def random_fortune() -> dict:
    f = random.choice(all_fortunes())
    logger.info("fortune.random.served", fortune_id=f.id)
    return {"id": f.id, "text": f.text, "author": f.author}


@app.get("/fortune/{fid}")
def specific_fortune(fid: int) -> dict:
    f = fortune_by_id(fid)
    if f is None:
        logger.warn("fortune.lookup.miss", fortune_id=fid)
        raise HTTPException(404, f"No fortune with id={fid}")
    logger.info("fortune.lookup.hit", fortune_id=fid)
    return {"id": f.id, "text": f.text, "author": f.author}


@app.get("/crash")
def crash() -> dict:
    logger.error("intentional.crash", reason="demo", kind="demo-500")
    # Intentional: gives Logan a repeatable error pattern.
    raise RuntimeError("swarm-lab: intentional crash for Logan's demo scan")
