/** Public campaign status - /api/stats/ */
export interface SiteStats {
  verified_total: string;
  verified_count: number;
  goals_scored: number;
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
  id: number;
  created: string;
}

/** An approved charity - /api/charities/ */
export interface Charity {
  id: number;
  name: string;
  url: string;
}
