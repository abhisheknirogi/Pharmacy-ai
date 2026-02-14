/** Global type definitions for PharmaRec AI */

export interface Medicine {
  id: number;
  name: string;
  generic_name?: string;
  batch_no: string;
  expiry_date?: string;
  stock_qty: number;
  reorder_level: number;
  price: number;
  manufacturer?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Sale {
  id: number;
  medicine_id?: number;
  medicine_name: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  sale_date: string;
  created_at: string;
}

export interface SaleSummary {
  medicine_name: string;
  total_quantity: number;
  total_amount: number;
  transaction_count: number;
}

export interface Pharmacy {
  id: number;
  name: string;
  address: string;
  phone?: string;
  email?: string;
  license_number?: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface ReorderSuggestion {
  medicine_id: number;
  medicine_name: string;
  current_stock: number;
  daily_average: number;
  suggested_order_qty: number;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  reorder_level: number;
}

export interface DailyRevenue {
  date: string;
  revenue: number;
  transactions: number;
}

export interface ApiError {
  status: number;
  detail: string;
}
