import React from 'react';
import clsx from 'clsx';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, title, description, children, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('bg-white rounded-lg border border-gray-200 shadow-sm', className)}
      {...props}
    >
      {(title || description) && (
        <div className="border-b border-gray-200 px-6 py-4">
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
          {description && <p className="text-sm text-gray-600 mt-1">{description}</p>}
        </div>
      )}
      <div className="px-6 py-4">{children}</div>
    </div>
  )
);

Card.displayName = 'Card';

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={clsx('px-6 py-4 border-b border-gray-200', className)} {...props} />
  )
);

CardHeader.displayName = 'CardHeader';

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={clsx('px-6 py-4', className)} {...props} />
  )
);

CardContent.displayName = 'CardContent';

export { Card, CardHeader, CardContent };
