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
  item_name: string;
  shop_name: string;
  amount: number;
  date: string;
  transaction_type: string;
  category: number;
}

export interface BillSummary {
  id: number;
  item_name: string;
  amount: number;
  due_date: string;
}

export interface OverviewSummary {
  total_balance: number;
  current_month: string;
  upcoming_bills: BillSummary[];
  recent_transactions: TransactionSummary[];
}
