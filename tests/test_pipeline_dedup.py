from webdominer.models import FailedPage, RejectedPage
from webdominer.pipeline import deduplicate_failed_pages, deduplicate_rejected_pages


def test_deduplicate_rejected_pages_keeps_single_normalized_url() -> None:
    pages = [
        RejectedPage(
            url="https://example.com/help?utm_source=google",
            reason="below_similarity_threshold:0.31",
            matched_keyword="doctor schedule",
            query='"doctor schedule"',
            title="Help page",
            similarity_score=0.31,
        ),
        RejectedPage(
            url="https://example.com/help",
            reason="below_similarity_threshold:0.44",
            matched_keyword="doctor schedule",
            query="doctor schedule healthcare clinic software workflow",
            title="Help page",
            similarity_score=0.44,
        ),
    ]

    deduped = deduplicate_rejected_pages(pages)

    assert len(deduped) == 1
    assert deduped[0].similarity_score == 0.44


def test_deduplicate_rejected_pages_prefers_record_with_similarity_score() -> None:
    pages = [
        RejectedPage(
            url="https://example.com/page",
            reason="below_min_word_count:40",
            matched_keyword="patient appointments",
            query='"patient appointments"',
            title="Short page",
            similarity_score=None,
        ),
        RejectedPage(
            url="https://example.com/page",
            reason="below_similarity_threshold:0.28",
            matched_keyword="patient appointments",
            query="patient appointments healthcare clinic software workflow",
            title="Short page",
            similarity_score=0.28,
        ),
    ]

    deduped = deduplicate_rejected_pages(pages)

    assert len(deduped) == 1
    assert deduped[0].similarity_score == 0.28


def test_deduplicate_failed_pages_deduplicates_same_url() -> None:
    pages = [
        FailedPage(
            url="https://example.com/article?utm_source=google",
            error="HTTPError: 403",
            matched_keyword="patient appointments",
            query='"patient appointments"',
        ),
        FailedPage(
            url="https://example.com/article",
            error="HTTPError: 403",
            matched_keyword="patient appointments",
            query="patient appointments healthcare clinic software workflow",
        ),
    ]

    deduped = deduplicate_failed_pages(pages)

    assert len(deduped) == 1
    assert deduped[0].url.startswith("https://example.com/article")


def test_deduplicate_failed_pages_keeps_distinct_search_failures_by_query() -> None:
    pages = [
        FailedPage(
            url="",
            error="search_failure:TimeoutError: timeout",
            matched_keyword="doctor schedule",
            query='"doctor schedule"',
        ),
        FailedPage(
            url="",
            error="search_failure:TimeoutError: timeout",
            matched_keyword="doctor schedule",
            query="doctor schedule healthcare clinic software workflow",
        ),
    ]

    deduped = deduplicate_failed_pages(pages)

    assert len(deduped) == 2