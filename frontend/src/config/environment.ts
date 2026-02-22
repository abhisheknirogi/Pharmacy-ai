/**
 * Environment and app configuration
 * Centralized configuration for frontend environment variables and app settings
 */

/**
 * API Configuration
 */
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // milliseconds
};

/**
 * App Configuration
 */
export const APP_CONFIG = {
  NAME: 'PharmaRec AI',
  VERSION: '1.0.0',
  ENVIRONMENT: process.env.NODE_ENV || 'development',
};

/**
 * Feature Flags
 */
export const FEATURES = {
  ENABLE_PDF_UPLOAD: true,
  ENABLE_AI_PREDICTIONS: true,
  ENABLE_SALES_IMPORT: true,
  ENABLE_ANALYTICS: true,
};

/**
 * UI Configuration
 */
export const UI_CONFIG = {
  ITEMS_PER_PAGE: 50,
  MAX_ITEMS_PER_PAGE: 1000,
  DEFAULT_THEME: 'light',
  TOAST_TIMEOUT: 5000, // milliseconds
};

/**
 * Error Configuration
 */
export const ERROR_CONFIG = {
  SHOW_ERROR_DETAILS: process.env.NODE_ENV === 'development',
  LOG_ERRORS: true,
  TRACK_ERRORS: process.env.NODE_ENV === 'production',
};

/**
 * Storage Configuration
 */
export const STORAGE_CONFIG = {
  TOKEN_KEY: 'auth_token',
  USER_KEY: 'auth_user',
  THEME_KEY: 'app_theme',
  PREFERENCES_KEY: 'user_preferences',
};

/**
 * Validation Configuration
 */
export const VALIDATION_CONFIG = {
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_MAX_LENGTH: 128,
  EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_PATTERN: /^\+?[\d\s\-()]+$/,
};

/**
 * Pagination Configuration
 */
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 50,
  MIN_LIMIT: 1,
  MAX_LIMIT: 1000,
};

/**
 * Check if running in development
 */
export const isDevelopment = () => process.env.NODE_ENV === 'development';

/**
 * Check if running in production
 */
export const isProduction = () => process.env.NODE_ENV === 'production';

/**
 * Get API URL
 */
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
