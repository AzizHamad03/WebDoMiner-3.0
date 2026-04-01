from webdominer.retrieval.url_filters import (
    get_url_domain,
    is_low_value_domain,
    is_probably_html_url,
    is_same_domain,
    normalize_url,
)
from webdominer.settings import Settings


def test_normalize_url_removes_fragment_and_tracking_params() -> None:
    url = (
        "https://Example.com/path/page/?utm_source=google&x=1#section"
    )
    normalized = normalize_url(url)
    assert normalized == "https://example.com/path/page?x=1"


def test_normalize_url_removes_default_port() -> None:
    url = "https://example.com:443/docs/"
    normalized = normalize_url(url)
    assert normalized == "https://example.com/docs"


def test_is_low_value_domain_blocks_known_noise_sites() -> None:
    assert is_low_value_domain("https://www.zhihu.com/question/123") is True
    assert is_low_value_domain("https://zhidao.baidu.com/question/456.html") is True
    assert is_low_value_domain("https://example.com/article") is False


def test_is_probably_html_url_accepts_reasonable_article_url() -> None:
    settings = Settings()
    url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8061456/"
    assert (
        is_probably_html_url(
            url=url,
            allowed_schemes=settings.allowed_schemes,
            bad_extensions=settings.bad_extensions,
            bad_url_patterns=settings.bad_url_patterns,
        )
        is True
    )


def test_is_probably_html_url_rejects_bad_extension() -> None:
    settings = Settings()
    url = "https://example.com/file.pdf"
    assert (
        is_probably_html_url(
            url=url,
            allowed_schemes=settings.allowed_schemes,
            bad_extensions=settings.bad_extensions,
            bad_url_patterns=settings.bad_url_patterns,
        )
        is False
    )


def test_is_probably_html_url_rejects_low_value_domain() -> None:
    settings = Settings()
    url = "https://www.zhihu.com/question/606095453"
    assert (
        is_probably_html_url(
            url=url,
            allowed_schemes=settings.allowed_schemes,
            bad_extensions=settings.bad_extensions,
            bad_url_patterns=settings.bad_url_patterns,
        )
        is False
    )


def test_get_url_domain_extracts_domain() -> None:
    assert get_url_domain("https://sub.example.com/path") == "sub.example.com"


def test_is_same_domain_detects_matching_domains() -> None:
    assert is_same_domain(
        "https://example.com/a",
        "https://example.com/b",
    ) is True
    assert is_same_domain(
        "https://example.com/a",
        "https://other.com/b",
    ) is False