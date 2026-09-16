import pytest

from pricing_engine.engine import PricingEngine, SoldOutError
from pricing_engine.models import BookingRequest, SeatTier, Show


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
