import pytest

from pricing_engine.models import SeatTier
from pricing_engine.price_import import (
    PriceParseError,
    build_seat_tiers,
    clean_price_list,
    normalize_tier_name,
    parse_price_to_paise,
)


def test_same_name_different_case_and_whitespace_is_deduplicated():
    report = clean_price_list(
        [
            {"tier_name": "  silver  ", "price": "500"},
            {"tier_name": "SILVER", "price": "500.00"},
            {"tier_name": " Silver ", "price": "500"},
        ]
    )

    assert report.imported == [{"tier_name": "Silver", "price_paise": 50000}]
    assert report.deduplicated == [
        {
            "tier_name": "Silver",
            "price_paise": 50000,
            "duplicate_count": 2,
            "reason": "same price repeated",
        }
    ]
    assert report.rejected == []


def test_conflicting_duplicate_keeps_first_valid_price():
    report = clean_price_list(
        [
            {"tier_name": "Gold", "price": "700"},
            {"tier_name": " gold ", "price": "800"},
        ]
    )

    assert report.imported == [{"tier_name": "Gold", "price_paise": 70000}]
    assert report.deduplicated == [
        {
            "tier_name": "Gold",
            "price_paise": 80000,
            "duplicate_count": 1,
            "reason": "duplicate name with conflicting price",
        }
    ]


def test_accepted_price_formats():
    assert parse_price_to_paise("500") == 50000
    assert parse_price_to_paise("500.00") == 50000
    assert parse_price_to_paise("₹500") == 50000
    assert parse_price_to_paise("Rs. 500") == 50000
    assert parse_price_to_paise("Rs.500") == 50000
    assert parse_price_to_paise("1,000") == 100000


def test_price_rounds_half_up_to_paise():
    assert parse_price_to_paise("10.125") == 1013


@pytest.mark.parametrize(
    ("raw_price", "message"),
    [
        ("   ", "blank price"),
        ("not-a-price", "unparseable price"),
        ("-500", "negative price"),
    ],
)
def test_invalid_prices_raise_distinct_errors(raw_price, message):
    with pytest.raises(PriceParseError, match=message):
        parse_price_to_paise(raw_price)


def test_invalid_prices_are_rejected_with_correct_reason():
    report = clean_price_list(
        [
            {"tier_name": "Silver", "price": "   "},
            {"tier_name": "Gold", "price": "abc"},
            {"tier_name": "Recliner", "price": "-100"},
        ]
    )

    assert report.imported == []
    assert report.deduplicated == []
    assert [entry["reason"] for entry in report.rejected] == [
        "blank price",
        "unparseable price",
        "negative price",
    ]


def test_realistic_messy_batch_counts_and_results():
    report = clean_price_list(
        [
            {"tier_name": "  silver ", "price": "₹500"},
            {"tier_name": "GOLD", "price": "1,000"},
            {"tier_name": "Silver", "price": "Rs. 500"},
            {"tier_name": " gold ", "price": "1200"},
            {"tier_name": "Recliner", "price": "2,500.00"},
            {"tier_name": "Balcony", "price": ""},
            {"tier_name": "Premium", "price": "unknown"},
            {"tier_name": "Free", "price": "-1"},
            {"tier_name": "RECLINER", "price": "2500"},
        ]
    )

    assert report.imported == [
        {"tier_name": "Silver", "price_paise": 50000},
        {"tier_name": "Gold", "price_paise": 100000},
        {"tier_name": "Recliner", "price_paise": 250000},
    ]
    assert len(report.deduplicated) == 3
    assert report.deduplicated[0]["reason"] == "same price repeated"
    assert report.deduplicated[1]["reason"] == "duplicate name with conflicting price"
    assert report.deduplicated[2]["reason"] == "same price repeated"
    assert len(report.rejected) == 3
    assert [entry["reason"] for entry in report.rejected] == [
        "blank price",
        "unparseable price",
        "negative price",
    ]


def test_rejected_duplicate_does_not_affect_valid_winner():
    report = clean_price_list(
        [
            {"tier_name": "Silver", "price": "bad"},
            {"tier_name": " silver ", "price": "500"},
        ]
    )

    assert report.imported == [{"tier_name": "Silver", "price_paise": 50000}]
    assert len(report.rejected) == 1
    assert report.rejected[0]["reason"] == "unparseable price"


def test_normalize_tier_name_collapses_whitespace_and_case():
    assert normalize_tier_name("  premium   recliner ") == "Premium Recliner"


def test_build_seat_tiers_from_imported_entries():
    imported = [
        {"tier_name": "Silver", "price_paise": 50000},
        {"tier_name": "Gold", "price_paise": 100000},
    ]

    tiers = build_seat_tiers(imported)

    assert tiers == [
        SeatTier("Silver", 50000, 0),
        SeatTier("Gold", 100000, 0),
    ]


def test_import_report_summary_includes_counts_and_rejections():
    report = clean_price_list(
        [
            {"tier_name": "Silver", "price": "500"},
            {"tier_name": "silver", "price": "500"},
            {"tier_name": "Gold", "price": ""},
        ]
    )

    summary = report.to_summary_string()
    assert "Imported: 1" in summary
    assert "Deduplicated: 1" in summary
    assert "Rejected: 1" in summary
    assert "Rejected row: blank price" in summary
