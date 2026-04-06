export interface BankAccount {
  id: number;
  account_type: string;
  account_name: string;
  bank_name: string;
  balance: number;
  masked_account_number?: string;
}

export interface TransactionSummary {
  id: number;
  description: string;
  amount: number;
  date: string;
}

export interface BillSummary {
  id: number;
  name: string;
  due_date: string;
}

export interface OverviewSummary {
  total_balance: number;
  current_month: string;
  upcoming_bills: BillSummary[];
  recent_transactions: TransactionSummary[];
}
