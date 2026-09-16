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
    show = Show(id="show-1", seat_tiers=[SeatTier("Silver", 15000, 100), SeatTier("Gold", 25000, 50)])
    booking = BookingRequest(show_id="show-1", quantities={"Silver": 2, "Gold": 1})
    assert PricingEngine().calculate_base_total(show, booking) == 55000


def test_sold_out_tier_raises_error_with_tier_name():
    show = Show(id="show-1", seat_tiers=[SeatTier("Recliner", 40000, 1)])
    booking = BookingRequest(show_id="show-1", quantities={"Recliner": 2})
    with pytest.raises(SoldOutError, match="Recliner"):
        PricingEngine().calculate_base_total(show, booking)


def test_requested_tier_not_offered_raises_error():
    show = Show(id="show-1", seat_tiers=[SeatTier("Silver", 15000, 100)])
    booking = BookingRequest(show_id="show-1", quantities={"Gold": 1})
    with pytest.raises(ValueError, match="Gold"):
        PricingEngine().calculate_base_total(show, booking)


def test_no_discounts():
    assert PricingEngine().apply_discounts(10000) == {"base_total": 10000, "festival_discount_applied": 0, "member_discount_applied": 0, "total_after_discounts": 10000}


def test_only_festival_discount():
    assert PricingEngine().apply_discounts(10000, FestivalDiscount(2500)) == {"base_total": 10000, "festival_discount_applied": 2500, "member_discount_applied": 0, "total_after_discounts": 7500}


def test_only_member_discount():
    assert PricingEngine().apply_discounts(10000, member_discount=MemberDiscount(10.0, 2000)) == {"base_total": 10000, "festival_discount_applied": 0, "member_discount_applied": 1000, "total_after_discounts": 9000}


def test_both_discounts_are_stacked_in_order():
    assert PricingEngine().apply_discounts(10000, FestivalDiscount(2000), MemberDiscount(10.0, 1000)) == {"base_total": 10000, "festival_discount_applied": 2000, "member_discount_applied": 800, "total_after_discounts": 7200}


def test_festival_discount_exceeding_total_clamps_to_zero():
    assert PricingEngine().apply_discounts(10000, FestivalDiscount(15000)) == {"base_total": 10000, "festival_discount_applied": 10000, "member_discount_applied": 0, "total_after_discounts": 0}


def test_member_discount_hits_cap():
    assert PricingEngine().apply_discounts(10000, member_discount=MemberDiscount(20.0, 1500)) == {"base_total": 10000, "festival_discount_applied": 0, "member_discount_applied": 1500, "total_after_discounts": 8500}


def test_final_bill_rounding_is_exact():
    discounts = PricingEngine().apply_discounts(101)
    bill = PricingEngine().calculate_final_bill(discounts, 1, FeeConfig(101), TaxConfig(18.0))
    assert bill["gst_on_tickets"] == 18
    assert bill["gst_on_fee"] == 18
    assert bill["grand_total"] == 238
    assert bill["total_after_discounts"] + bill["convenience_fee"] + bill["gst_on_tickets"] + bill["gst_on_fee"] == bill["grand_total"]


def test_zero_discount_booking_final_bill():
    bill = PricingEngine().calculate_final_bill(PricingEngine().apply_discounts(10000), 2, FeeConfig(100), TaxConfig(18.0))
    assert bill == {"base_total": 10000, "festival_discount": 0, "member_discount": 0, "total_after_discounts": 10000, "convenience_fee": 200, "gst_on_tickets": 1800, "gst_on_fee": 36, "grand_total": 12036}


def test_heavily_discounted_booking():
    engine = PricingEngine()
    discounts = engine.apply_discounts(100000, FestivalDiscount(70000), MemberDiscount(50.0, 10000))
    bill = engine.calculate_final_bill(discounts, 4, FeeConfig(250), TaxConfig(18.0))
    assert bill["total_after_discounts"] == 20000
    assert bill["grand_total"] == 24780


def test_large_multi_tier_booking():
    engine = PricingEngine()
    show = Show("large-show", [SeatTier("Silver", 10000, 500), SeatTier("Gold", 20000, 500), SeatTier("Recliner", 35000, 200)])
    booking = BookingRequest("large-show", {"Silver": 100, "Gold": 75, "Recliner": 25})
    discounts = engine.apply_discounts(engine.calculate_base_total(show, booking), FestivalDiscount(50000), MemberDiscount(10.0, 100000))
    bill = engine.calculate_final_bill(discounts, 200, FeeConfig(50), TaxConfig(18.0))
    assert bill["base_total"] == 2875000
    assert bill["total_after_discounts"] == 2542500
    assert bill["grand_total"] == 3032100


def test_receipt_is_human_readable_and_ends_with_total():
    engine = PricingEngine()
    bill = engine.calculate_final_bill(engine.apply_discounts(10000), 1, FeeConfig(100), TaxConfig(18.0))
    lines = engine.render_receipt(bill).splitlines()
    assert lines[-1] == "Total: 11918 paise"
    assert len(lines) == 8


def test_booking_exactly_at_remaining_inventory_succeeds():
    show = Show("show", [SeatTier("Silver", 10000, 3)])
    booking = BookingRequest("show", {"Silver": 3})
    assert PricingEngine().calculate_base_total(show, booking) == 30000


def test_booking_one_more_than_remaining_inventory_is_sold_out():
    show = Show("show", [SeatTier("Silver", 10000, 3)])
    booking = BookingRequest("show", {"Silver": 4})
    with pytest.raises(SoldOutError, match="Silver"):
        PricingEngine().calculate_base_total(show, booking)


def test_member_discount_cap_exactly_equals_percentage_amount():
    result = PricingEngine().apply_discounts(10000, member_discount=MemberDiscount(10.0, 1000))
    assert result["member_discount_applied"] == 1000
    assert result["total_after_discounts"] == 9000


def test_zero_quantity_booking_raises_clear_validation_error():
    show = Show("show", [SeatTier("Silver", 10000, 10)])
    booking = BookingRequest("show", {"Silver": 0})
    with pytest.raises(ValueError, match="greater than zero"):
        PricingEngine().calculate_base_total(show, booking)


def test_zero_price_tier_with_fee_and_gst():
    engine = PricingEngine()
    show = Show("show", [SeatTier("Comp", 0, 2)])
    booking = BookingRequest("show", {"Comp": 2})
    bill = price_booking(show, booking, None, None, FeeConfig(100), TaxConfig(18.0))
    assert bill["base_total"] == 0
    assert bill["convenience_fee"] == 200
    assert bill["gst_on_tickets"] == 0
    assert bill["gst_on_fee"] == 36
    assert bill["grand_total"] == 236


def test_zero_gst_rate_tax_holiday():
    engine = PricingEngine()
    discounts = engine.apply_discounts(10000)
    bill = engine.calculate_final_bill(discounts, 2, FeeConfig(100), TaxConfig(0.0))
    assert bill["gst_on_tickets"] == 0
    assert bill["gst_on_fee"] == 0
    assert bill["grand_total"] == 10200
