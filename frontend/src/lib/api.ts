import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ApiError } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response?.status === 401) {
          // Clear token on 401
          this.setToken(null);
          // Optionally redirect to login
          typeof window !== 'undefined' && window.location.replace('/login');
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  // Auth endpoints
  async register(email: string, password: string, full_name?: string) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      full_name,
    });
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {
      email,
      password,
    });
    const { access_token } = response.data;
    this.setToken(access_token);
    return response.data;
  }

  async getMe() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Inventory endpoints
  async getMedicines(skip = 0, limit = 100) {
    const response = await this.client.get('/inventory/', {
      params: { skip, limit },
    });
    return response.data;
  }

  async searchMedicines(query: string) {
    const response = await this.client.get('/inventory/search', {
      params: { q: query },
    });
    return response.data;
  }

  async getExpiringMedicines(days = 30) {
    const response = await this.client.get('/inventory/expiring', {
      params: { days },
    });
    return response.data;
  }

  async getLowStockMedicines() {
    const response = await this.client.get('/inventory/low-stock');
    return response.data;
  }

  async getMedicine(id: number) {
    const response = await this.client.get(`/inventory/${id}`);
    return response.data;
  }

  async createMedicine(data: any) {
    const response = await this.client.post('/inventory/', data);
    return response.data;
  }

  async updateMedicine(id: number, data: any) {
    const response = await this.client.put(`/inventory/${id}`, data);
    return response.data;
  }

  async deleteMedicine(id: number) {
    await this.client.delete(`/inventory/${id}`);
  }

  // Sales endpoints
  async recordSale(data: any) {
    const response = await this.client.post('/sales/', data);
    return response.data;
  }

  async getSales(skip = 0, limit = 100, days = 30) {
    const response = await this.client.get('/sales/', {
      params: { skip, limit, days },
    });
    return response.data;
  }

  async getSalesSummary(days = 30) {
    const response = await this.client.get('/sales/summary', {
      params: { days },
    });
    return response.data;
  }

  async getDailyRevenue(days = 30) {
    const response = await this.client.get('/sales/daily-revenue', {
      params: { days },
    });
    return response.data;
  }

  async uploadSalesFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/sales/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // Reorder endpoints
  async getReorderSuggestions(days = 7) {
    const response = await this.client.get('/reorder/suggestions', {
      params: { days },
    });
    return response.data;
  }

  async predictReorder(medicineId: number, daysAhead = 7) {
    const response = await this.client.get(`/reorder/predict/${medicineId}`, {
      params: { days_ahead: daysAhead },
    });
    return response.data;
  }

  async getReorderAnalysis() {
    const response = await this.client.get('/reorder/analysis');
    return response.data;
  }

  // PDF Parser endpoints
  async parsePdf(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/pdf/parse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
