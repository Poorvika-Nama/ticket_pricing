import type { ImportReportData, Receipt, SeatTier } from "./types";

// In development, Vite proxies /api to the local FastAPI server.
// Set VITE_API_BASE_URL only when the API is hosted somewhere else.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request<T>(path: string, init: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    });
  } catch {
    throw new Error(
      "Unable to connect to the pricing API. Make sure FastAPI is running on http://127.0.0.1:8000."
    );
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // Keep the useful HTTP status when the server does not return JSON.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export type BookingPayload = {
  show: { id: string; seat_tiers: SeatTier[] };
  booking_request: { show_id: string; quantities: Record<string, number> };
  festival_discount: { flat_amount_paise: number } | null;
  member_discount: { percentage: number; cap_paise: number } | null;
  fee_config: { per_ticket_fee_paise: number };
  tax_config: { gst_rate_percent: number };
};

export function priceBooking(payload: BookingPayload) {
  return request<Receipt>("/price-booking", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function importPriceList(rows: Array<{ tier_name: string; price: unknown }>) {
  return request<ImportReportData>("/import-price-list", {
    method: "POST",
    body: JSON.stringify(rows),
  });
}
