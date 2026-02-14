'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function InventoryPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!isAuthenticated) router.push('/login');
  }, [isAuthenticated, router]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['medicines', searchQuery],
    queryFn: () => (searchQuery ? apiClient.searchMedicines(searchQuery) : apiClient.getMedicines()),
    enabled: !!isAuthenticated,
  });

  if (!isAuthenticated) return <div>Redirecting...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Inventory Management</h1>
        <p className="text-gray-600 mt-2">Manage your pharmacy medicines</p>
      </div>

      <Card className="mb-8">
        <div className="flex gap-4 items-center">
          <input
            type="text"
            placeholder="Search medicines by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1"
          />
          <Button>Add Medicine</Button>
        </div>
      </Card>

      {error && (
        <div className="alert alert-error mb-4">
          <p>Error loading medicines</p>
        </div>
      )}

      <Card>
        {isLoading ? (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading medicines...</p>
          </div>
        ) : data && data.length > 0 ? (
          <div className="overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Batch</th>
                  <th>Stock</th>
                  <th>Price</th>
                  <th>Expiry</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.map((med: any) => (
                  <tr key={med.id}>
                    <td className="font-medium">{med.name}</td>
                    <td>{med.batch_no}</td>
                    <td>
                      <span className={`font-bold ${med.stock_qty <= med.reorder_level ? 'text-red-600' : 'text-green-600'}`}>
                        {med.stock_qty}
                      </span>
                    </td>
                    <td>₹{med.price.toFixed(2)}</td>
                    <td>{med.expiry_date ? new Date(med.expiry_date).toLocaleDateString() : 'N/A'}</td>
                    <td>
                      <Button variant="ghost" size="sm">Edit</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No medicines found</p>
          </div>
        )}
      </Card>
    </div>
  );
}
