"""Bound every dependency response before materializing its JSON."""

import asyncio

import httpx

from .contracts import JsonDict


class ResponseLimit(ValueError):
    pass


async def bounded_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    deadline: float,
    body: JsonDict | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    async with asyncio.timeout(deadline):
        async with client.stream(
            method,
            url,
            json=body,
            timeout=deadline,
            headers={"Accept-Encoding": "identity", **(headers or {})},
        ) as response:
            # Local JSON integrations have no compression contract. Reject it before decoding.
            if response.headers.get("content-encoding", "identity").lower() != "identity":
                raise ResponseLimit("unsupported_response_encoding")
            content = bytearray()
            async for chunk in response.aiter_bytes():
                if len(content) + len(chunk) > 32768:
                    raise ResponseLimit("oversized_response")
                content.extend(chunk)
            return httpx.Response(
                response.status_code,
                headers=response.headers,
                content=bytes(content),
                request=response.request,
            )
