import asyncio

import httpx
import pytest

from switchlane import AsyncSwitchlane, Switchlane, SwitchlaneError


ROUTE_RESPONSE = {
    "recommendations": [],
    "task_profile": {
        "category": "unknown",
        "subcategory": None,
        "language": None,
        "input_type": None,
        "output_type": None,
        "complexity": "medium",
        "keywords": [],
    },
    "meta": {
        "match_path": "llm_intent",
        "candidates_evaluated": 0,
        "elapsed_ms": 5,
        "abstained": True,
        "abstention_reason": "no_candidates",
        "confidence": None,
    },
}


@pytest.mark.parametrize("base_url", [None, "https://example.test/"])
def test_sync_route_parses_abstention_and_sends_auth(base_url: str | None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer sl_live_test"
        assert str(request.url) == f"{(base_url or 'https://switchlane.ai').rstrip('/')}/v1/route"
        return httpx.Response(200, json=ROUTE_RESPONSE)

    options = {"base_url": base_url} if base_url is not None else {}
    with Switchlane("sl_live_test", transport=httpx.MockTransport(handler), **options) as client:
        result = client.route("unknown task")

    assert result.meta.abstained is True
    assert result.meta.abstention_reason == "no_candidates"


def test_sync_errors_include_status_and_body() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(401, json={"error": "Invalid API key"}))
    with Switchlane("bad", base_url="https://example.test", transport=transport) as client:
        with pytest.raises(SwitchlaneError) as caught:
            client.usage()

    assert caught.value.status_code == 401
    assert caught.value.body == {"error": "Invalid API key"}


@pytest.mark.parametrize("base_url", [None, "https://example.test/"])
def test_async_route(base_url: str | None) -> None:
    async def run() -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url) == f"{(base_url or 'https://switchlane.ai').rstrip('/')}/v1/route"
            return httpx.Response(200, json=ROUTE_RESPONSE)

        options = {"base_url": base_url} if base_url is not None else {}
        async with AsyncSwitchlane(
            "sl_live_test",
            transport=httpx.MockTransport(handler),
            **options,
        ) as client:
            result = await client.route("unknown task")
        assert result.meta.confidence is None

    asyncio.run(run())
