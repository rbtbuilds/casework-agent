import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest

from casework_agent.config import Settings
from casework_agent.contracts import Order
from casework_agent.tools import DependencyError, ReadTools


class OversizedStream(httpx.AsyncByteStream):
    def __init__(self) -> None:
        self.received = 0
        self.closed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for _ in range(100):
            self.received += 1024
            yield b"x" * 1024

    async def aclose(self) -> None:
        self.closed = True


async def test_dependency_body_is_stopped_at_the_limit(tmp_path: Path) -> None:
    stream = OversizedStream()
    tools = ReadTools("c", "o", Settings(root=tmp_path))
    await tools.client.aclose()
    tools.client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=stream))
    )
    try:
        with pytest.raises(DependencyError):
            await tools.read("http://dependency/order", Order)
        assert stream.received <= 33792
        assert stream.closed
    finally:
        await tools.close()


class DripStream(httpx.AsyncByteStream):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        for _ in range(900):
            await asyncio.sleep(0.01)
            yield b" "


async def test_dependency_request_has_a_total_deadline(tmp_path: Path) -> None:
    tools = ReadTools("c", "o", Settings(root=tmp_path))
    await tools.client.aclose()
    tools.client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=DripStream()))
    )
    try:
        async with asyncio.timeout(8):
            with pytest.raises(DependencyError):
                await tools.read("http://dependency/order", Order)
    finally:
        await tools.close()
