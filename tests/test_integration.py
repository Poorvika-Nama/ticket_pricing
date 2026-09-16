from pricing_engine.engine import PricingEngine, price_booking
from pricing_engine.models import (
    BookingRequest,
    FestivalDiscount,
    FeeConfig,
    MemberDiscount,
    SeatTier,
    Show,
    TaxConfig,
)


def test_full_booking_with_all_pricing_layers_and_receipt():
    show = Show(
        id="integration-show",
        seat_tiers=[
            SeatTier("Silver", 15000, 100),
            SeatTier("Gold", 25000, 50),
            SeatTier("Recliner", 40000, 20),
        ],
    )
    booking = BookingRequest(
        show_id="integration-show",
        quantities={"Silver": 2, "Gold": 1, "Recliner": 1},
    )

    breakdown = price_booking(
        show,
        booking,
        FestivalDiscount(flat_amount_paise=2000),
        MemberDiscount(percentage=10.0, cap_paise=3000),
        FeeConfig(per_ticket_fee_paise=500),
        TaxConfig(gst_rate_percent=18.0),
    )

    assert breakdown == {
        "base_total": 95000,
        "festival_discount": 2000,
        "member_discount": 9300,
        "total_after_discounts": 83700,
        "convenience_fee": 2000,
        "gst_on_tickets": 15066,
        "gst_on_fee": 360,
        "grand_total": 101126,
    }

    receipt = PricingEngine().render_receipt(breakdown)
    assert receipt.splitlines() == [
        "Base total: 95000 paise",
        "Festival discount: 2000 paise",
        "Member discount: 9300 paise",
        "Total after discounts: 83700 paise",
        "Convenience fee: 2000 paise",
        "GST on tickets: 15066 paise",
        "GST on fee: 360 paise",
        "Total: 101126 paise",
    ]


def test_full_booking_with_no_discounts():
    show = Show(
        id="no-discount-show",
        seat_tiers=[SeatTier("Silver", 10000, 10), SeatTier("Gold", 20000, 10)],
    )
    booking = BookingRequest(
        show_id="no-discount-show",
        quantities={"Silver": 1, "Gold": 1},
    )

    breakdown = price_booking(
        show,
        booking,
        None,
        None,
        FeeConfig(per_ticket_fee_paise=100),
        TaxConfig(gst_rate_percent=18.0),
    )

    assert breakdown["grand_total"] == 32036
    assert breakdown["base_total"] == 30000
    assert breakdown["convenience_fee"] == 200
