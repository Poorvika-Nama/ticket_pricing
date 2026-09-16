from .models import BookingRequest, Show


class SoldOutError(Exception):
    """Raised when a requested seat tier does not have enough seats."""


class PricingEngine:
    def calculate_base_total(self, show: Show, booking_request: BookingRequest) -> int:
        """Calculate the base ticket total in paise, without discounts or fees."""
        tiers = {tier.name: tier for tier in show.seat_tiers}

        for tier_name, quantity in booking_request.quantities.items():
            if tier_name not in tiers:
                raise ValueError(f"Tier '{tier_name}' is not offered on this show")

            tier = tiers[tier_name]
            if tier.available_seats < quantity:
                raise SoldOutError(tier_name)

        return sum(
            tiers[tier_name].price_paise * quantity
            for tier_name, quantity in booking_request.quantities.items()
        )
