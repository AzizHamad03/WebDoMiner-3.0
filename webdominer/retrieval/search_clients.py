from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import requests
from duckduckgo_search import DDGS

from webdominer.models import SearchResult
from webdominer.settings import Settings


class BaseSearchClient(ABC):
    """
    Abstract interface for search backends.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    def search(
        self,
        keyword: str,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        """
        Run a search query and return normalized SearchResult objects.
        """
        raise NotImplementedError


class DuckDuckGoSearchClient(BaseSearchClient):
    """
    Search backend using duckduckgo-search.
    """

    def search(
        self,
        keyword: str,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        results: list[SearchResult] = []

        with DDGS() as ddgs:
            raw_items = ddgs.text(
                keywords=query,
                max_results=max_results,
            )

            for rank, item in enumerate(raw_items, start=1):
                url = (item.get("href") or "").strip()
                title = (item.get("title") or "").strip()
                snippet = (item.get("body") or "").strip()

                if not url:
                    continue

                results.append(
                    SearchResult(
                        keyword=keyword,
                        query=query,
                        title=title,
                        snippet=snippet,
                        url=url,
                        rank=rank,
                        source="ddg",
                    )
                )

        return results


class SearxNGSearchClient(BaseSearchClient):
    """
    Search backend using a self-hosted SearxNG instance.
    """

    def search(
        self,
        keyword: str,
        query: str,
        max_results: int,
    ) -> list[SearchResult]:
        if not self.settings.searxng_base_url:
            raise ValueError(
                "SearxNG backend selected, but searxng_base_url is not configured."
            )

        base_url = self.settings.searxng_base_url.rstrip("/")
        endpoint = f"{base_url}/search"

        response = requests.get(
            endpoint,
            params={
                "q": query,
                "format": "json",
                "language": "en",
                "safesearch": 0,
            },
            timeout=self.settings.request_timeout_seconds,
            headers={"User-Agent": self.settings.user_agent},
        )
        response.raise_for_status()

        payload: dict[str, Any] = response.json()
        raw_items = payload.get("results", [])

        results: list[SearchResult] = []
        for rank, item in enumerate(raw_items[:max_results], start=1):
            url = (item.get("url") or "").strip()
            title = (item.get("title") or "").strip()
            snippet = (item.get("content") or "").strip()

            if not url:
                continue

            results.append(
                SearchResult(
                    keyword=keyword,
                    query=query,
                    title=title,
                    snippet=snippet,
                    url=url,
                    rank=rank,
                    source="searxng",
                )
            )

        return results


def create_search_client(settings: Settings) -> BaseSearchClient:
    """
    Factory function that returns the configured search client.
    """
    backend = settings.search_backend.strip().lower()

    if backend == "ddg":
        return DuckDuckGoSearchClient(settings)
    if backend == "searxng":
        return SearxNGSearchClient(settings)

    raise ValueError(
        f"Unsupported search backend: {settings.search_backend!r}. "
        "Supported values are 'ddg' and 'searxng'."
    )