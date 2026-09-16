import pytest

from pricing_engine.engine import PricingEngine, SoldOutError
from pricing_engine.models import (
    BookingRequest,
    FestivalDiscount,
    FeeConfig,
    MemberDiscount,
    SeatTier,
    Show,
    TaxConfig,
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


def test_final_bill_rounding_is_exact():
    discounts = PricingEngine().apply_discounts(101)
    bill = PricingEngine().calculate_final_bill(
        discounts,
        ticket_count=1,
        fee_config=FeeConfig(per_ticket_fee_paise=101),
        tax_config=TaxConfig(gst_rate_percent=18.0),
    )

    assert bill["gst_on_tickets"] == 18
    assert bill["gst_on_fee"] == 18
    assert bill["grand_total"] == 238
    assert (
        bill["total_after_discounts"]
        + bill["convenience_fee"]
        + bill["gst_on_tickets"]
        + bill["gst_on_fee"]
        == bill["grand_total"]
    )


def test_zero_discount_booking_final_bill():
    engine = PricingEngine()
    discounts = engine.apply_discounts(10000)
    bill = engine.calculate_final_bill(
        discounts,
        ticket_count=2,
        fee_config=FeeConfig(per_ticket_fee_paise=100),
        tax_config=TaxConfig(gst_rate_percent=18.0),
    )

    assert bill == {
        "base_total": 10000,
        "festival_discount": 0,
        "member_discount": 0,
        "total_after_discounts": 10000,
        "convenience_fee": 200,
        "gst_on_tickets": 1800,
        "gst_on_fee": 36,
        "grand_total": 12036,
    }


def test_heavily_discounted_booking():
    engine = PricingEngine()
    discounts = engine.apply_discounts(
        100000,
        FestivalDiscount(flat_amount_paise=70000),
        MemberDiscount(percentage=50.0, cap_paise=10000),
    )
    bill = engine.calculate_final_bill(
        discounts,
        ticket_count=4,
        fee_config=FeeConfig(per_ticket_fee_paise=250),
        tax_config=TaxConfig(gst_rate_percent=18.0),
    )

    assert bill["total_after_discounts"] == 20000
    assert bill["convenience_fee"] == 1000
    assert bill["gst_on_tickets"] == 3600
    assert bill["gst_on_fee"] == 180
    assert bill["grand_total"] == 24780


def test_large_multi_tier_booking():
    engine = PricingEngine()
    show = Show(
        id="large-show",
        seat_tiers=[
            SeatTier("Silver", 10000, 500),
            SeatTier("Gold", 20000, 500),
            SeatTier("Recliner", 35000, 200),
        ],
    )
    booking = BookingRequest(
        show_id="large-show",
        quantities={"Silver": 100, "Gold": 75, "Recliner": 25},
    )
    base = engine.calculate_base_total(show, booking)
    discounts = engine.apply_discounts(
        base,
        FestivalDiscount(flat_amount_paise=50000),
        MemberDiscount(percentage=10.0, cap_paise=100000),
    )
    bill = engine.calculate_final_bill(
        discounts,
        ticket_count=200,
        fee_config=FeeConfig(per_ticket_fee_paise=50),
        tax_config=TaxConfig(gst_rate_percent=18.0),
    )

    assert bill["base_total"] == 2875000
    assert bill["total_after_discounts"] == 2542500
    assert bill["grand_total"] == 3032100
    assert (
        bill["total_after_discounts"]
        + bill["convenience_fee"]
        + bill["gst_on_tickets"]
        + bill["gst_on_fee"]
        == bill["grand_total"]
    )


def test_receipt_is_human_readable_and_ends_with_total():
    engine = PricingEngine()
    discounts = engine.apply_discounts(10000)
    bill = engine.calculate_final_bill(
        discounts,
        ticket_count=1,
        fee_config=FeeConfig(per_ticket_fee_paise=100),
        tax_config=TaxConfig(gst_rate_percent=18.0),
    )

    receipt = engine.render_receipt(bill)
    lines = receipt.splitlines()

    assert lines == [
        "Base total: 10000 paise",
        "Festival discount: 0 paise",
        "Member discount: 0 paise",
        "Total after discounts: 10000 paise",
        "Convenience fee: 100 paise",
        "GST on tickets: 1800 paise",
        "GST on fee: 18 paise",
        "Total: 11918 paise",
    ]
    assert lines[-1] == "Total: 11918 paise"
