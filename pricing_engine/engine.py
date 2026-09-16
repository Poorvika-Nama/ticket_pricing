from decimal import Decimal, ROUND_HALF_UP

from .models import BookingRequest, FestivalDiscount, MemberDiscount, Show


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

    def apply_discounts(
        self,
        base_total_paise: int,
        festival_discount: FestivalDiscount | None = None,
        member_discount: MemberDiscount | None = None,
    ) -> dict[str, int]:
        """Apply festival discount first, then capped member discount."""
        festival_discount_applied = 0
        remaining = base_total_paise

        if festival_discount is not None:
            festival_discount_applied = min(
                festival_discount.flat_amount_paise, remaining
            )
            remaining -= festival_discount_applied

        member_discount_applied = 0
        if member_discount is not None:
            percentage_discount = (
                Decimal(str(member_discount.percentage)) * Decimal(remaining) / Decimal(100)
            ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            member_discount_applied = min(
                int(percentage_discount), member_discount.cap_paise, remaining
            )
            remaining -= member_discount_applied

        return {
            "base_total": base_total_paise,
            "festival_discount_applied": festival_discount_applied,
            "member_discount_applied": member_discount_applied,
            "total_after_discounts": remaining,
        }
