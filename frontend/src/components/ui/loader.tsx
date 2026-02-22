import React from 'react';

export const Loader: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }[size];

  return (
    <div className={`${sizeClasses} border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin`} />
  );
};

export const Skeleton: React.FC<{ className?: string; count?: number }> = ({ className = 'h-4 w-full', count = 1 }) => {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`${className} bg-gray-200 rounded animate-pulse`} />
      ))}
    </div>
  );
};

export const LoadingSpinner: React.FC = () => (
  <div className="flex items-center justify-center p-8">
    <Loader size="lg" />
  </div>
);

export default { Loader, Skeleton, LoadingSpinner };
