from dataclasses import dataclass


@dataclass
class SeatTier:
    name: str
    price_paise: int
    available_seats: int


@dataclass
class Show:
    id: str
    seat_tiers: list[SeatTier]


@dataclass
class BookingRequest:
    show_id: str
    quantities: dict[str, int]
