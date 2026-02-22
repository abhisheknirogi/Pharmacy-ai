import React from 'react';

interface TableProps {
  children: React.ReactNode;
  className?: string;
}

const Table: React.FC<TableProps> = ({ children, className = '' }) => (
  <div className="w-full overflow-x-auto">
    <table className={`w-full border-collapse ${className}`}>
      {children}
    </table>
  </div>
);

const TableHead: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <thead className={`bg-gray-100 border-b border-gray-200 ${className}`}>
    {children}
  </thead>
);

const TableBody: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <tbody className={className}>
    {children}
  </tbody>
);

const TableRow: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <tr className={`border-b border-gray-200 hover:bg-gray-50 ${className}`}>
    {children}
  </tr>
);

const TableHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <th className={`px-6 py-3 text-left text-sm font-semibold text-gray-700 ${className}`}>
    {children}
  </th>
);

const TableCell: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <td className={`px-6 py-4 text-sm text-gray-700 ${className}`}>
    {children}
  </td>
);

export { Table, TableHead, TableBody, TableRow, TableHeader, TableCell };
