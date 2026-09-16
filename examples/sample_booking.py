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


show = Show(
    id="sample-show",
    seat_tiers=[
        SeatTier(name="Silver", price_paise=15000, available_seats=100),
        SeatTier(name="Gold", price_paise=25000, available_seats=50),
        SeatTier(name="Recliner", price_paise=40000, available_seats=20),
    ],
)

booking_request = BookingRequest(
    show_id="sample-show",
    quantities={"Silver": 2, "Gold": 1, "Recliner": 1},
)

festival_discount = FestivalDiscount(flat_amount_paise=2000)
member_discount = MemberDiscount(percentage=10.0, cap_paise=3000)
fee_config = FeeConfig(per_ticket_fee_paise=500)
tax_config = TaxConfig(gst_rate_percent=18.0)

breakdown = price_booking(
    show,
    booking_request,
    festival_discount,
    member_discount,
    fee_config,
    tax_config,
)

print(PricingEngine().render_receipt(breakdown))
