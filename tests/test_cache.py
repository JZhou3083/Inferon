import pytest

def test_cache_miss_then_hit(client, cache):
    prompt = "test 1"

    # ensure cache empty
    cache.clear()

    # first request → should miss cache
    r1 = client.post("/generate", json={"prompt": prompt})
    assert r1.status_code == 200
    assert r1.json()["cache_hit"] is False

    # second request → should hit cache
    r2 = client.post("/generate", json={"prompt": prompt})
    assert r2.status_code == 200
    assert r2.json()["cache_hit"] is True

    # responses should match
    assert r1.json()["response"] == r2.json()["response"]