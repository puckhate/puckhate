/** Public campaign status - /api/stats/ */
export interface SiteStats {
  verified_total: string;
  verified_count: number;
  largest_donation: string | null;
  charities_donated_to: number;
  goals_scored: number;
  ca_exchange_rate: string;
}

/** Current exchange rate - /api/exchange-rate/ */
export interface ExchangeRate {
  ca_exchange_rate: string;
}

/** A verified donation - /api/donations/ */
export interface Donation {
  id: number;
  created: string;
  amount: string;
  name: string;
  charity: string;
}

/** A receipt created from an upload - POST /api/receipts/ */
export interface DonationReceipt {
  token: string;
  created: string;
}

/** An approved charity - /api/charities/ */
export interface Charity {
  id: number;
  name: string;
  url: string;
}
