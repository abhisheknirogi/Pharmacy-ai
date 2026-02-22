/**
 * API client with interceptors for authentication, error handling, and request/response logging
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import type {
  ApiResponse,
  PaginatedResponse,
  Medicine,
  MedicineCreateRequest,
  MedicineUpdateRequest,
  Sale,
  SaleCreateRequest,
  User,
  AuthToken,
  ReorderSuggestion,
  ExpiryAlert,
} from '@/types';
import { ApiErrorHandler, logError, parseApiError } from '@/utils/error-handler';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const REQUEST_TIMEOUT = 30000; // 30 seconds

/**
 * API Client class with full type safety and error handling
 */
class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;
  private requestId: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: REQUEST_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }

        // Generate request ID
        this.requestId = this.generateRequestId();
        config.headers['X-Request-ID'] = this.requestId;

        return config;
      },
      (error) => {
        logError('Request interceptor', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Success response
        return response;
      },
      (error: AxiosError) => {
        // Handle error response
        const apiError = this.handleError(error);
        return Promise.reject(apiError);
      }
    );

    // Load token from localStorage
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Handle API errors uniformly
   */
  private handleError(error: AxiosError): ApiErrorHandler {
    if (error.response) {
      const { status, data } = error.response;
      const errorData = data as Record<string, unknown>;

      // Handle 401 - Unauthorized
      if (status === 401) {
        this.setToken(null);
        if (typeof window !== 'undefined') {
          window.location.replace('/login');
        }
      }

      return new ApiErrorHandler(
        status,
        (errorData.error as string) || 'ERROR',
        (errorData.message as string) || 'An error occurred',
        errorData.details as Record<string, unknown>,
        errorData.request_id as string
      );
    }

    if (error.request) {
      // Request made but no response received
      return new ApiErrorHandler(
        500,
        'NETWORK_ERROR',
        'Network error: No response from server'
      );
    }

    // Error in request setup
    return new ApiErrorHandler(500, 'CLIENT_ERROR', error.message || 'An unknown error occurred');
  }

  /**
   * Set authentication token
   */
  setToken(token: string | null): void {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  /**
   * Get authentication token
   */
  getToken(): string | null {
    return this.token;
  }

  /**
   * Check if authenticated
   */
  isAuthenticated(): boolean {
    return !!this.token;
  }

  // ==================== AUTH ENDPOINTS ====================

  async register(
    email: string,
    password: string,
    full_name?: string
  ): Promise<ApiResponse<User>> {
    const response = await this.client.post<ApiResponse<User>>('/auth/register', {
      email,
      password,
      full_name,
    });
    return response.data;
  }

  async login(email: string, password: string): Promise<AuthToken> {
    const response = await this.client.post<AuthToken>('/auth/login', {
      email,
      password,
    });
    if (response.data.access_token) {
      this.setToken(response.data.access_token);
    }
    return response.data;
  }

  async getMe(): Promise<ApiResponse<User>> {
    const response = await this.client.get<ApiResponse<User>>('/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.setToken(null);
    }
  }

  // ==================== INVENTORY ENDPOINTS ====================

  async getMedicines(skip = 0, limit = 100): Promise<PaginatedResponse<Medicine>> {
    const response = await this.client.get<PaginatedResponse<Medicine>>('/inventory/', {
      params: { skip, limit },
    });
    return response.data;
  }

  async searchMedicines(query: string, skip = 0, limit = 100): Promise<PaginatedResponse<Medicine>> {
    const response = await this.client.get<PaginatedResponse<Medicine>>('/inventory/search', {
      params: { q: query, skip, limit },
    });
    return response.data;
  }

  async getExpiringMedicines(days = 30): Promise<ApiResponse<ExpiryAlert[]>> {
    const response = await this.client.get<ApiResponse<ExpiryAlert[]>>('/inventory/expiring', {
      params: { days },
    });
    return response.data;
  }

  async getLowStockMedicines(): Promise<PaginatedResponse<Medicine>> {
    const response = await this.client.get<PaginatedResponse<Medicine>>('/inventory/low-stock');
    return response.data;
  }

  async getMedicine(id: number): Promise<ApiResponse<Medicine>> {
    const response = await this.client.get<ApiResponse<Medicine>>(`/inventory/${id}`);
    return response.data;
  }

  async createMedicine(data: MedicineCreateRequest): Promise<ApiResponse<Medicine>> {
    const response = await this.client.post<ApiResponse<Medicine>>('/inventory/', data);
    return response.data;
  }

  async updateMedicine(
    id: number,
    data: MedicineUpdateRequest
  ): Promise<ApiResponse<Medicine>> {
    const response = await this.client.put<ApiResponse<Medicine>>(`/inventory/${id}`, data);
    return response.data;
  }

  async deleteMedicine(id: number): Promise<void> {
    await this.client.delete(`/inventory/${id}`);
  }

  // ==================== SALES ENDPOINTS ====================

  async recordSale(data: SaleCreateRequest): Promise<ApiResponse<Sale>> {
    const response = await this.client.post<ApiResponse<Sale>>('/sales/', data);
    return response.data;
  }

  async getSales(skip = 0, limit = 100, days = 30): Promise<PaginatedResponse<Sale>> {
    const response = await this.client.get<PaginatedResponse<Sale>>('/sales/', {
      params: { skip, limit, days },
    });
    return response.data;
  }

  async getSalesSummary(days = 30): Promise<ApiResponse<Record<string, unknown>[]>> {
    const response = await this.client.get<ApiResponse<Record<string, unknown>[]>>(
      '/sales/summary',
      {
        params: { days },
      }
    );
    return response.data;
  }

  async getDailyRevenue(days = 30): Promise<ApiResponse<Record<string, number>[]>> {
    const response = await this.client.get<ApiResponse<Record<string, number>[]>>(
      '/sales/daily-revenue',
      {
        params: { days },
      }
    );
    return response.data;
  }

  async uploadSalesFile(file: File): Promise<ApiResponse<Record<string, unknown>>> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post<ApiResponse<Record<string, unknown>>>(
      '/sales/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  }

  // ==================== REORDER ENDPOINTS ====================

  async getReorderSuggestions(days = 7): Promise<ApiResponse<ReorderSuggestion[]>> {
    const response = await this.client.get<ApiResponse<ReorderSuggestion[]>>(
      '/reorder/suggestions',
      {
        params: { days },
      }
    );
    return response.data;
  }

  async predictReorder(
    medicineId: number,
    daysAhead = 7
  ): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await this.client.get<ApiResponse<Record<string, unknown>>>(
      `/reorder/predict/${medicineId}`,
      {
        params: { days_ahead: daysAhead },
      }
    );
    return response.data;
  }

  async getReorderAnalysis(): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await this.client.get<ApiResponse<Record<string, unknown>>>(
      '/reorder/analysis'
    );
    return response.data;
  }

  // ==================== PDF PARSER ENDPOINTS ====================

  async parsePdf(file: File): Promise<ApiResponse<Record<string, unknown>>> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post<ApiResponse<Record<string, unknown>>>(
      '/pdf/parse',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  }

  // ==================== HEALTH & DIAGNOSTICS ====================

  async getHealth(): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await this.client.get<ApiResponse<Record<string, unknown>>>('/health');
    return response.data;
  }

  async getVersion(): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await this.client.get<ApiResponse<Record<string, unknown>>>('/version');
    return response.data;
  }

  async getDiagnostics(): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await this.client.get<ApiResponse<Record<string, unknown>>>(
      '/diagnostics'
    );
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

