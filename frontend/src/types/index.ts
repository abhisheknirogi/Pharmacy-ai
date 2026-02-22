/**
 * Global type definitions for PharmaRec AI
 * Comprehensive TypeScript types for API responses, data models, and component props
 */

/** ============================================================================ 
 * API Response Types
 * ============================================================================ */

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  status_code?: number;
  request_id?: string;
}

export interface PaginationMeta {
  current_page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  meta: PaginationMeta;
  message?: string;
}

export interface ApiError {
  status: number;
  error: string;
  message: string;
  details?: Record<string, unknown>;
  request_id?: string;
}

/** ============================================================================ 
 * Medicine Types
 * ============================================================================ */

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

export interface MedicineCreateRequest {
  name: string;
  generic_name?: string;
  batch_no: string;
  expiry_date?: string;
  stock_qty: number;
  reorder_level?: number;
  price: number;
  manufacturer?: string;
  description?: string;
}

export interface MedicineUpdateRequest {
  name?: string;
  generic_name?: string;
  batch_no?: string;
  expiry_date?: string;
  stock_qty?: number;
  reorder_level?: number;
  price?: number;
  manufacturer?: string;
  description?: string;
}

export interface MedicineFilter {
  q?: string;
  skip?: number;
  limit?: number;
}

/** ============================================================================ 
 * Sales Types
 * ============================================================================ */

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

export interface SaleCreateRequest {
  medicine_id: number;
  quantity: number;
  unit_price: number;
}

export interface SaleSummary {
  medicine_name: string;
  total_quantity: number;
  total_amount: number;
  transaction_count: number;
}

export interface DailyRevenue {
  date: string;
  revenue: number;
  transactions: number;
}

/** ============================================================================ 
 * Pharmacy Types
 * ============================================================================ */

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

export interface PharmacyCreateRequest {
  name: string;
  address: string;
  phone?: string;
  email?: string;
  license_number?: string;
}

/** ============================================================================ 
 * User & Authentication Types
 * ============================================================================ */

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface UserCreateRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface TokenData {
  email?: string;
  exp?: number;
}

/** ============================================================================ 
 * Reorder & Prediction Types
 * ============================================================================ */

export interface ReorderSuggestion {
  medicine_id: number;
  medicine_name: string;
  current_stock: number;
  daily_average: number;
  suggested_order_qty: number;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  reorder_level: number;
}

export interface ExpiryAlert {
  id: number;
  medicine_id: number;
  medicine_name: string;
  expiry_date: string;
  batch_no: string;
  quantity: number;
  days_until_expiry: number;
}

/** ============================================================================ 
 * Loading & UI State Types
 * ============================================================================ */

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  state: LoadingState;
  data?: T;
  error?: ApiError;
}

export interface FormState {
  isDirty: boolean;
  isSubmitting: boolean;
  errors: Record<string, string>;
}

/** ============================================================================ 
 * Table & List Types
 * ============================================================================ */

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: unknown) => React.ReactNode;
}

export interface FilterOption {
  value: string;
  label: string;
}

/** ============================================================================ 
 * Health & Diagnostics Types
 * ============================================================================ */

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  app: string;
  version: string;
  timestamp: string;
}

export interface Diagnostics {
  status: 'ok' | 'degraded' | 'error';
  app: string;
  version: string;
  memory_usage_mb: number;
  cpu_percent: number;
  timestamp: string;
  database_configured: boolean;
  ml_enabled: boolean;
  pdf_parsing_enabled: boolean;
}
