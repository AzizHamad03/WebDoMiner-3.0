from webdominer.models import SearchResult
from webdominer.retrieval.discovery import (
    UrlDiscoveryService,
    compute_domain_diversity_penalty,
    compute_rank_bonus,
    compute_text_overlap_score,
)
from webdominer.settings import Settings


class DummySearchClient:
    def search(self, keyword: str, query: str, max_results: int):
        return []


def test_compute_text_overlap_score_rewards_keyword_match() -> None:
    strong_score = compute_text_overlap_score(
        keyword="patient appointments scheduling",
        title="Patient appointments scheduling workflow in healthcare",
        snippet="This article explains patient scheduling and clinic workflows.",
        query='"patient appointments scheduling"',
    )
    weak_score = compute_text_overlap_score(
        keyword="patient appointments scheduling",
        title="Random article about gardening",
        snippet="Plants, watering, and soil.",
        query='"patient appointments scheduling"',
    )

    assert strong_score > weak_score


def test_compute_rank_bonus_prefers_better_rank() -> None:
    assert compute_rank_bonus(1) > compute_rank_bonus(5)
    assert compute_rank_bonus(5) >= compute_rank_bonus(20)


def test_compute_domain_diversity_penalty_increases_for_later_domain_results() -> None:
    assert compute_domain_diversity_penalty(1) == 0.0
    assert compute_domain_diversity_penalty(2) > 0.0
    assert compute_domain_diversity_penalty(4) >= compute_domain_diversity_penalty(2)


def test_discover_urls_deduplicates_same_normalized_url() -> None:
    settings = Settings()
    service = UrlDiscoveryService(settings, DummySearchClient())

    raw_results = [
        SearchResult(
            keyword="patient appointments scheduling",
            query='"patient appointments scheduling"',
            title="Patient scheduling workflow",
            snippet="A useful article on patient scheduling workflow.",
            url="https://example.com/article?utm_source=google",
            rank=2,
            source="ddg",
        ),
        SearchResult(
            keyword="patient appointments scheduling",
            query="patient appointments scheduling healthcare clinic software workflow",
            title="Patient scheduling workflow in clinics",
            snippet="An even better article on patient appointments scheduling.",
            url="https://example.com/article",
            rank=1,
            source="ddg",
        ),
    ]

    discovered = service.discover_urls(raw_results)

    assert len(discovered) == 1
    assert discovered[0].url == "https://example.com/article"


def test_discover_urls_filters_low_value_domain() -> None:
    settings = Settings()
    service = UrlDiscoveryService(settings, DummySearchClient())

    raw_results = [
        SearchResult(
            keyword="patient appointments scheduling",
            query='"patient appointments scheduling"',
            title="Zhihu result",
            snippet="Noise result",
            url="https://www.zhihu.com/question/123",
            rank=1,
            source="ddg",
        ),
        SearchResult(
            keyword="patient appointments scheduling",
            query='"patient appointments scheduling"',
            title="Useful healthcare article",
            snippet="Strong patient scheduling article",
            url="https://example.com/healthcare-workflow",
            rank=2,
            source="ddg",
        ),
    ]

    discovered = service.discover_urls(raw_results)

    assert len(discovered) == 1
    assert discovered[0].url == "https://example.com/healthcare-workflow"


def test_discover_urls_prefers_better_scored_duplicate() -> None:
    settings = Settings()
    service = UrlDiscoveryService(settings, DummySearchClient())

    raw_results = [
        SearchResult(
            keyword="doctor schedule",
            query='"doctor schedule"',
            title="Weak result",
            snippet="Short generic snippet.",
            url="https://example.com/schedule",
            rank=5,
            source="ddg",
        ),
        SearchResult(
            keyword="doctor schedule",
            query="doctor schedule healthcare clinic software workflow",
            title="Doctor schedule workflow for clinics",
            snippet="Detailed clinic scheduling and physician calendar workflow.",
            url="https://example.com/schedule",
            rank=1,
            source="ddg",
        ),
    ]

    discovered = service.discover_urls(raw_results)

    assert len(discovered) == 1
    assert discovered[0].title == "Doctor schedule workflow for clinics"
    assert discovered[0].search_rank == 1