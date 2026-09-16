from fastapi.testclient import TestClient

from pricing_engine.api import app


client = TestClient(app)


def _booking_payload() -> dict:
    return {
        "show": {
            "id": "show-1",
            "seat_tiers": [
                {"name": "Silver", "price_paise": 15000, "available_seats": 10},
                {"name": "Gold", "price_paise": 25000, "available_seats": 5},
            ],
        },
        "booking_request": {"show_id": "show-1", "quantities": {"Silver": 2, "Gold": 1}},
        "festival_discount": {"flat_amount_paise": 2000},
        "member_discount": {"percentage": 10.0, "cap_paise": 3000},
        "fee_config": {"per_ticket_fee_paise": 500},
        "tax_config": {"gst_rate_percent": 18.0},
    }


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_successful_booking_returns_itemized_paise_and_rupees() -> None:
    response = client.post("/price-booking", json=_booking_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["base_total"] == {"paise": 55000, "rupees": "₹550.00"}
    assert body["festival_discount"] == {"paise": 2000, "rupees": "₹20.00"}
    assert body["member_discount"] == {"paise": 3000, "rupees": "₹30.00"}
    assert body["total_after_discounts"] == {"paise": 50000, "rupees": "₹500.00"}
    assert body["convenience_fee"] == {"paise": 1500, "rupees": "₹15.00"}
    assert body["gst_on_tickets"] == {"paise": 9000, "rupees": "₹90.00"}
    assert body["gst_on_fee"] == {"paise": 270, "rupees": "₹2.70"}
    assert body["grand_total"] == {"paise": 60770, "rupees": "₹607.70"}


def test_sold_out_tier_returns_4xx_with_clear_error() -> None:
    payload = _booking_payload()
    payload["booking_request"]["quantities"] = {"Gold": 6}
    response = client.post("/price-booking", json=payload)
    assert response.status_code == 409
    assert "Gold" in response.json()["detail"]
    assert "Not enough seats available" in response.json()["detail"]


def test_import_price_list_returns_mixed_clean_report() -> None:
    rows = [
        {"tier_name": " silver ", "price": "500"},
        {"tier_name": "SILVER", "price": "500.00"},
        {"tier_name": "Gold", "price": "₹750"},
        {"tier_name": "Gold", "price": "800"},
        {"tier_name": "Recliner", "price": ""},
        {"tier_name": "Balcony", "price": "not-a-price"},
        {"tier_name": "VIP", "price": "-100"},
    ]
    response = client.post("/import-price-list", json=rows)
    assert response.status_code == 200
    body = response.json()
    assert len(body["imported"]) == 2
    assert len(body["deduplicated"]) == 2
    assert len(body["rejected"]) == 3
    assert body["imported"] == [
        {"tier_name": "Silver", "price_paise": 50000},
        {"tier_name": "Gold", "price_paise": 75000},
    ]
    assert body["deduplicated"][0]["reason"] == "same price repeated"
    assert body["deduplicated"][1]["reason"] == "duplicate name with conflicting price"
    assert [item["reason"] for item in body["rejected"]] == [
        "blank price", "unparseable price", "negative price"
    ]
