/**
 * Error handling utilities for consistent error management
 */

import { ApiError } from '@/types';

/**
 * Custom error class for API errors
 */
export class ApiErrorHandler extends Error {
  constructor(
    public status: number,
    public error: string,
    message: string,
    public details?: Record<string, unknown>,
    public request_id?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }

  toJSON() {
    return {
      status: this.status,
      error: this.error,
      message: this.message,
      details: this.details,
      request_id: this.request_id,
    };
  }
}

/**
 * Parse API error response
 */
export const parseApiError = (error: unknown): ApiError => {
  if (error instanceof ApiErrorHandler) {
    return {
      status: error.status,
      error: error.error,
      message: error.message,
      details: error.details,
      request_id: error.request_id,
    };
  }

  if (error instanceof Error) {
    return {
      status: 500,
      error: 'INTERNAL_ERROR',
      message: error.message,
    };
  }

  if (typeof error === 'object' && error !== null) {
    const errorObj = error as Record<string, unknown>;
    return {
      status: (errorObj.status as number) || 500,
      error: (errorObj.error as string) || 'UNKNOWN_ERROR',
      message: (errorObj.message as string) || 'An unexpected error occurred',
      details: errorObj.details as Record<string, unknown>,
      request_id: errorObj.request_id as string,
    };
  }

  return {
    status: 500,
    error: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred',
  };
};

/**
 * Get user-friendly error message
 */
export const getUserErrorMessage = (error: ApiError): string => {
  const statusMessages: Record<number, string> = {
    400: 'Invalid request. Please check your input.',
    401: 'Authentication failed. Please log in again.',
    403: 'You do not have permission to perform this action.',
    404: 'Resource not found.',
    409: 'This resource already exists.',
    422: 'Please check your input and try again.',
    429: 'Too many requests. Please try again later.',
    500: 'An internal server error occurred. Please try again later.',
    503: 'Service temporarily unavailable. Please try again later.',
  };

  return statusMessages[error.status] || error.message || 'An unexpected error occurred';
};

/**
 * Check if error is retryable
 */
export const isRetryableError = (error: ApiError): boolean => {
  const retryableStatuses = [408, 429, 500, 502, 503, 504];
  return retryableStatuses.includes(error.status);
};

/**
 * Retry logic with exponential backoff
 */
export const withRetry = async <T,>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> => {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError || new Error('Max retries exceeded');
};

/**
 * Logger for errors with context
 */
export const logError = (context: string, error: unknown): void => {
  const timestamp = new Date().toISOString();
  const apiError = parseApiError(error);

  const logEntry = {
    timestamp,
    context,
    status: apiError.status,
    error: apiError.error,
    message: apiError.message,
    details: apiError.details,
    request_id: apiError.request_id,
  };

  if (process.env.NODE_ENV === 'development') {
    console.error('[ERROR]', logEntry);
  } else {
    // Send to error tracking service in production
    // Example: Sentry, LogRocket, etc.
    console.error('[ERROR]', logEntry);
  }
};
