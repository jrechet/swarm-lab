"""Tests for swarm-lab. One is intentionally flaky — gives FlakyBot signal."""

from __future__ import annotations

import os
import random

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_fortune_random_returns_valid_entry():
    r = client.get("/fortune")
    assert r.status_code == 200
    body = r.json()
    assert 1 <= body["id"] <= 5
    assert body["text"]


def test_fortune_by_id():
    r = client.get("/fortune/1")
    assert r.status_code == 200
    assert "Knuth" in r.json()["author"]


def test_fortune_not_found():
    r = client.get("/fortune/999")
    assert r.status_code == 404


def test_crash_endpoint_raises_500():
    # TestClient re-raises by default; check that it does fail.
    with pytest.raises(RuntimeError):
        client.get("/crash")


@pytest.mark.skipif(
    os.environ.get("FLAKY_OFF") == "1",
    reason="set FLAKY_OFF=1 to disable the intentional flake",
)
def test_intentionally_flaky_random_timing():
    # 1-in-4 fail rate. Over a week of CI runs this trips FlakyBot's threshold.
    if random.randint(0, 3) == 0:
        pytest.fail("intentional flake — exercises FlakyBot")
