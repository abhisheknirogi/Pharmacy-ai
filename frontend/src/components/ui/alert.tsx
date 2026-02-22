import React from 'react';

interface AlertProps {
  children: React.ReactNode;
  variant?: 'success' | 'error' | 'warning' | 'info';
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({ children, variant = 'info', className = '' }) => {
  const bgColor = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    info: 'bg-blue-50 border-blue-200',
  }[variant];

  const textColor = {
    success: 'text-green-800',
    error: 'text-red-800',
    warning: 'text-yellow-800',
    info: 'text-blue-800',
  }[variant];

  return (
    <div className={`border rounded-lg p-4 ${bgColor} ${textColor} ${className}`}>
      {children}
    </div>
  );
};

export default Alert;
