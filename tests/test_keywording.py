from webdominer.retrieval.keywording import (
    contains_document_noise,
    contains_weak_context,
    count_tokens,
    is_strong_keyword_candidate,
    normalize_phrase,
)


def test_normalize_phrase_removes_basic_noise() -> None:
    phrase = "  Patient-Appointments / Scheduling!!  "
    assert normalize_phrase(phrase) == "patient appointments scheduling"


def test_normalize_phrase_rejects_document_title_noise() -> None:
    phrase = "ClinicFlow Requirements Specification"
    assert normalize_phrase(phrase) == ""


def test_strong_keyword_candidate_accepts_good_healthcare_phrase() -> None:
    assert is_strong_keyword_candidate("patient appointments scheduling") is True


def test_strong_keyword_candidate_accepts_two_word_domain_phrase() -> None:
    assert is_strong_keyword_candidate("doctor schedule") is True


def test_strong_keyword_candidate_rejects_document_noise_phrase() -> None:
    assert is_strong_keyword_candidate("requirements specification") is False


def test_strong_keyword_candidate_rejects_awkward_domain_action_domain_pattern() -> None:
    assert is_strong_keyword_candidate("appointment track patient") is False


def test_strong_keyword_candidate_rejects_awkward_domain_weak_domain_pattern() -> None:
    assert is_strong_keyword_candidate("appointment priority clinic") is False


def test_strong_keyword_candidate_rejects_awkward_domain_weak_weak_pattern() -> None:
    assert is_strong_keyword_candidate("doctor utilization room") is False


def test_strong_keyword_candidate_rejects_generic_single_word() -> None:
    assert is_strong_keyword_candidate("system") is False


def test_contains_document_noise_counts_correctly() -> None:
    assert contains_document_noise("clinicflow requirements specification") == 3


def test_contains_weak_context_counts_correctly() -> None:
    assert contains_weak_context("doctor utilization room") == 2


def test_count_tokens_counts_words() -> None:
    assert count_tokens("patient appointments scheduling") == 3