import pytest

from pricing_engine.engine import PricingEngine, SoldOutError
from pricing_engine.models import (
    BookingRequest,
    FestivalDiscount,
    MemberDiscount,
    SeatTier,
    Show,
)


def test_normal_multi_tier_booking():
    show = Show(
        id="show-1",
        seat_tiers=[
            SeatTier(name="Silver", price_paise=15000, available_seats=100),
            SeatTier(name="Gold", price_paise=25000, available_seats=50),
        ],
    )
    booking = BookingRequest(
        show_id="show-1",
        quantities={"Silver": 2, "Gold": 1},
    )

    assert PricingEngine().calculate_base_total(show, booking) == 55000


def test_sold_out_tier_raises_error_with_tier_name():
    show = Show(
        id="show-1",
        seat_tiers=[SeatTier(name="Recliner", price_paise=40000, available_seats=1)],
    )
    booking = BookingRequest(show_id="show-1", quantities={"Recliner": 2})

    with pytest.raises(SoldOutError, match="Recliner"):
        PricingEngine().calculate_base_total(show, booking)


def test_requested_tier_not_offered_raises_error():
    show = Show(
        id="show-1",
        seat_tiers=[SeatTier(name="Silver", price_paise=15000, available_seats=100)],
    )
    booking = BookingRequest(show_id="show-1", quantities={"Gold": 1})

    with pytest.raises(ValueError, match="Gold"):
        PricingEngine().calculate_base_total(show, booking)


def test_no_discounts():
    result = PricingEngine().apply_discounts(10000)

    assert result == {
        "base_total": 10000,
        "festival_discount_applied": 0,
        "member_discount_applied": 0,
        "total_after_discounts": 10000,
    }


def test_only_festival_discount():
    result = PricingEngine().apply_discounts(
        10000, FestivalDiscount(flat_amount_paise=2500)
    )

    assert result == {
        "base_total": 10000,
        "festival_discount_applied": 2500,
        "member_discount_applied": 0,
        "total_after_discounts": 7500,
    }


def test_only_member_discount():
    result = PricingEngine().apply_discounts(
        10000, member_discount=MemberDiscount(percentage=10.0, cap_paise=2000)
    )

    assert result == {
        "base_total": 10000,
        "festival_discount_applied": 0,
        "member_discount_applied": 1000,
        "total_after_discounts": 9000,
    }


def test_both_discounts_are_stacked_in_order():
    result = PricingEngine().apply_discounts(
        10000,
        FestivalDiscount(flat_amount_paise=2000),
        MemberDiscount(percentage=10.0, cap_paise=1000),
    )

    assert result == {
        "base_total": 10000,
        "festival_discount_applied": 2000,
        "member_discount_applied": 800,
        "total_after_discounts": 7200,
    }


def test_festival_discount_exceeding_total_clamps_to_zero():
    result = PricingEngine().apply_discounts(
        10000, FestivalDiscount(flat_amount_paise=15000)
    )

    assert result == {
        "base_total": 10000,
        "festival_discount_applied": 10000,
        "member_discount_applied": 0,
        "total_after_discounts": 0,
    }


def test_member_discount_hits_cap():
    result = PricingEngine().apply_discounts(
        10000, member_discount=MemberDiscount(percentage=20.0, cap_paise=1500)
    )

    assert result == {
        "base_total": 10000,
        "festival_discount_applied": 0,
        "member_discount_applied": 1500,
        "total_after_discounts": 8500,
    }
