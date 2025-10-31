"""Web search tool."""

from __future__ import annotations

import functools
import logging
from typing import Literal

import anyio
from ddgs import DDGS
from pydantic import TypeAdapter
from pydantic_ai import RunContext
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


class SearchResult(TypedDict):
    """A web search result."""

    title: str
    """The title of the search result."""

    href: str
    """The URL of the search result."""

    body: str
    """The snippet/description of the search result."""


_search_result_adapter = TypeAdapter(list[SearchResult])


async def web_search(
    ctx: RunContext[None],
    query: str,
    *,
    max_results: int,
    region: str,
    timelimit: Literal["d", "w", "m", "y"] | None,
) -> list[SearchResult]:
    """Search the web for information.

    The agent should infer appropriate parameters from the query context:
    - max_results: Fewer (2) for quick facts, more for research, default to 6
    - region: Based on query language/location mentions. Defaults to 'ww-en'
    - timelimit: Recent for news/trends, None for general knowledge

    Args:
        ctx: Agent run context
        query: The search query
        max_results: Maximum number of results
        region: Region code (e.g., 'us-en', 'ww-en', 'ww-es').
        timelimit: Time limit ('d'=day, 'w'=week, 'm'=month, 'y'=year)

    Returns:
        List of search results with title, URL, and snippet.

    Examples:
        >>> # Agent should infer: max_results=5, region='ww-en', timelimit=None
        >>> await web_search(ctx, "what is Python")

        >>> # Agent should infer: max_results=10, region='us-en', timelimit='w'
        >>> await web_search(ctx, "latest US tech news")

        >>> # Agent should infer: max_results=2, region='ww-es', timelimit=None
        >>> await web_search(ctx, "¿Quién fue Dante Alighieri?")
    """

    logger.info(
        "Searching: query=%r, max_results=%d, region=%r, timelimit=%r",
        query,
        max_results,
        region,
        timelimit,
    )

    client = DDGS()

    search_func = functools.partial(
        client.text,
        query,
        region=region,
        safesearch="moderate",
        timelimit=timelimit,
        max_results=max_results,
        backend="auto",
    )

    # Run in thread pool (DDGS is sync)
    results = await anyio.to_thread.run_sync(search_func)

    return _search_result_adapter.validate_python(results)
