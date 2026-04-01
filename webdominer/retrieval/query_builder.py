from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SearchQuery:
    """
    A search-ready query built from a cleaned keyword phrase.
    """

    keyword: str
    query: str
    strategy: str  # e.g. "exact_phrase", "broad_domain", "article_focused"

    def to_dict(self) -> dict:
        return {
            "keyword": self.keyword,
            "query": self.query,
            "strategy": self.strategy,
        }


class QueryBuilder:
    """
    Build search-engine-friendly queries from cleaned keyword phrases.

    We do not want to search raw phrases blindly. Instead, we generate a small
    set of useful query forms that improve recall while keeping relevance high.
    """

    def build_queries_for_keyword(self, keyword: str) -> list[SearchQuery]:
        """
        Build a small set of search queries for one keyword.

        Current strategy:
        1. Exact phrase query
        2. Broad web article / guide query
        3. Domain concept query
        """
        keyword = keyword.strip()
        if not keyword:
            return []

        queries: list[SearchQuery] = []

        # Highest precision.
        queries.append(
            SearchQuery(
                keyword=keyword,
                query=f'"{keyword}"',
                strategy="exact_phrase",
            )
        )

        # Good for pages that explain or discuss the concept.
        queries.append(
            SearchQuery(
                keyword=keyword,
                query=f'{keyword} guide overview best practices',
                strategy="article_focused",
            )
        )

        # Better for domain and implementation-oriented material.
        queries.append(
            SearchQuery(
                keyword=keyword,
                query=f'{keyword} workflow system process requirements',
                strategy="broad_domain",
            )
        )

        return queries

    def build_queries(self, keywords: list[str]) -> list[SearchQuery]:
        """
        Build queries for all keywords and flatten them into one list.
        """
        all_queries: list[SearchQuery] = []
        seen: set[tuple[str, str]] = set()

        for keyword in keywords:
            for item in self.build_queries_for_keyword(keyword):
                key = (item.keyword, item.query)
                if key in seen:
                    continue
                seen.add(key)
                all_queries.append(item)

        return all_queries