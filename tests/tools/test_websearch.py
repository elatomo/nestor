from unittest.mock import MagicMock, patch

import pytest

from nestor.config import settings
from nestor.tools.websearch import web_search


@pytest.fixture
def ddgs():
    with patch("nestor.tools.websearch.DDGS") as MockDDGS:
        ddgs = MagicMock()
        MockDDGS.return_value = ddgs
        yield ddgs


@pytest.fixture
def search_results():
    """Sample search results from DDGS."""
    return [
        {
            "title": "Python Programming Guide",
            "href": "https://example.com/python",
            "body": "Learn Python programming basics and advanced concepts.",
        },
        {
            "title": "Python Tutorial",
            "href": "https://tutorial.com/python",
            "body": "Step-by-step Python tutorial for beginners.",
        },
    ]


class TestWebSearch:
    """Tests for web_search function."""

    @pytest.mark.asyncio
    async def test_successful_search(self, ctx, ddgs, search_results):
        """Should return validated search results."""
        ddgs.text.return_value = search_results
        results = await web_search(
            ctx,
            "Python programming",
            max_results=5,
            region="ww-en",
            timelimit=None,
        )

        assert len(results) == 2
        assert results[0]["title"] == "Python Programming Guide"
        assert results[0]["href"] == "https://example.com/python"
        assert "body" in results[0]

        ddgs.text.assert_called_once_with(
            "Python programming",
            region="ww-en",
            safesearch="moderate",
            timelimit=None,
            max_results=5,
            backend=settings.search_backend,
        )

    @pytest.mark.asyncio
    async def test_search_with_timelimit(self, ctx, ddgs, search_results):
        """Should pass timelimit parameter to DDGS."""
        ddgs.text.return_value = search_results

        await web_search(
            ctx,
            "Latest news",
            max_results=10,
            region="us-en",
            timelimit="w",
        )

        call_kwargs = ddgs.text.call_args[1]
        assert call_kwargs["timelimit"] == "w"

    @pytest.mark.asyncio
    async def test_empty_results(self, ctx, ddgs):
        """Should handle empty results gracefully."""
        ddgs.text.return_value = []

        results = await web_search(
            ctx,
            "Quantum pineapple teleportation method",
            max_results=5,
            region="ww-en",
            timelimit=None,
        )

        assert results == []
