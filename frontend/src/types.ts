export type SeatTier = {
  name: string;
  price_paise: number;
  available_seats: number;
};

export type MoneyLineItem = { paise: number; rupees: string };

export type Receipt = {
  base_total: MoneyLineItem;
  festival_discount: MoneyLineItem;
  member_discount: MoneyLineItem;
  total_after_discounts: MoneyLineItem;
  convenience_fee: MoneyLineItem;
  gst_on_tickets: MoneyLineItem;
  gst_on_fee: MoneyLineItem;
  grand_total: MoneyLineItem;
};

export type ImportedEntry = { tier_name: string; price_paise: number };
export type DeduplicatedEntry = {
  tier_name: string;
  price_paise: number;
  duplicate_count: number;
  reason: string;
};
export type RejectedEntry = { raw_row: Record<string, unknown>; reason: string };
export type ImportReportData = {
  imported: ImportedEntry[];
  deduplicated: DeduplicatedEntry[];
  rejected: RejectedEntry[];
};
