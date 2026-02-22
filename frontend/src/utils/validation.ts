/**
 * Input validation utilities for form and API data validation
 */

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

/**
 * Email validation regex
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validates email format
 */
export const validateEmail = (email: string): boolean => {
  return EMAIL_REGEX.test(email);
};

/**
 * Validates password strength
 */
export const validatePassword = (password: string): { isValid: boolean; message?: string } => {
  if (password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters' };
  }
  if (!/[A-Z]/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one uppercase letter' };
  }
  if (!/[a-z]/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one lowercase letter' };
  }
  if (!/[0-9]/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one digit' };
  }
  return { isValid: true };
};

/**
 * Validates required field
 */
export const validateRequired = (value: unknown): boolean => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined && value !== '';
};

/**
 * Validates string length
 */
export const validateLength = (
  value: string,
  min: number,
  max: number
): { isValid: boolean; message?: string } => {
  const length = value.trim().length;
  if (length < min) {
    return { isValid: false, message: `Must be at least ${min} characters` };
  }
  if (length > max) {
    return { isValid: false, message: `Must be no more than ${max} characters` };
  }
  return { isValid: true };
};

/**
 * Validates number range
 */
export const validateRange = (
  value: number,
  min: number,
  max: number
): { isValid: boolean; message?: string } => {
  if (value < min || value > max) {
    return { isValid: false, message: `Value must be between ${min} and ${max}` };
  }
  return { isValid: true };
};

/**
 * Validates number is positive
 */
export const validatePositive = (value: number): { isValid: boolean; message?: string } => {
  if (value <= 0) {
    return { isValid: false, message: 'Value must be positive' };
  }
  return { isValid: true };
};

/**
 * Sanitizes user input to prevent XSS
 */
export const sanitizeInput = (input: string): string => {
  return input
    .trim()
    .replace(/[<>\"']/g, (char) => {
      const escapeMap: Record<string, string> = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
      };
      return escapeMap[char] || char;
    });
};

/**
 * Validates medicine create/update request
 */
export const validateMedicineForm = (data: {
  name?: string;
  batch_no?: string;
  stock_qty?: number;
  price?: number;
}): ValidationResult => {
  const errors: Record<string, string> = {};

  if (!data.name || !validateRequired(data.name)) {
    errors.name = 'Medicine name is required';
  } else {
    const nameLengthResult = validateLength(data.name, 1, 255);
    if (!nameLengthResult.isValid) {
      errors.name = nameLengthResult.message || 'Invalid name length';
    }
  }

  if (!data.batch_no || !validateRequired(data.batch_no)) {
    errors.batch_no = 'Batch number is required';
  }

  if (data.stock_qty !== undefined) {
    const stockValidation = validateRange(data.stock_qty, 0, 1000000);
    if (!stockValidation.isValid) {
      errors.stock_qty = 'Stock quantity must be between 0 and 1000000';
    }
  }

  if (data.price !== undefined) {
    const priceValidation = validatePositive(data.price);
    if (!priceValidation.isValid) {
      errors.price = priceValidation.message || 'Price must be positive';
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

/**
 * Validates user registration form
 */
export const validateUserRegistration = (data: {
  email?: string;
  password?: string;
  confirmPassword?: string;
  full_name?: string;
}): ValidationResult => {
  const errors: Record<string, string> = {};

  if (!data.email || !validateRequired(data.email)) {
    errors.email = 'Email is required';
  } else if (!validateEmail(data.email)) {
    errors.email = 'Invalid email format';
  }

  if (!data.password) {
    errors.password = 'Password is required';
  } else {
    const passwordValidation = validatePassword(data.password);
    if (!passwordValidation.isValid) {
      errors.password = passwordValidation.message || 'Password does not meet requirements';
    }
  }

  if (data.confirmPassword !== data.password) {
    errors.confirmPassword = 'Passwords do not match';
  }

  if (data.full_name) {
    const nameValidation = validateLength(data.full_name, 1, 255);
    if (!nameValidation.isValid) {
      errors.full_name = nameValidation.message || 'Invalid name length';
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};
