'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function ReorderPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) router.push('/login');
  }, [isAuthenticated, router]);

  const { data, isLoading } = useQuery({
    queryKey: ['reorder_suggestions'],
    queryFn: () => apiClient.getReorderSuggestions(7),
    enabled: !!isAuthenticated,
  });

  if (!isAuthenticated) return <div>Redirecting...</div>;

  const suggestions = data?.data || [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Reorder Suggestions</h1>
      <p className="text-gray-600 mb-8">AI-powered inventory reorder recommendations</p>

      {isLoading ? (
        <Card>
          <p className="text-center py-8 text-gray-500">Loading recommendations...</p>
        </Card>
      ) : suggestions.length > 0 ? (
        <div className="space-y-4">
          {suggestions.map((item: any) => (
            <Card key={item.medicine_id}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{item.medicine_name}</h3>
                  <div className="grid grid-cols-2 gap-4 mt-2 text-sm text-gray-600">
                    <p>Current Stock: <span className="font-bold text-gray-900">{item.current_stock}</span></p>
                    <p>Daily Average: <span className="font-bold text-gray-900">{item.daily_average}</span></p>
                    <p>Suggested Order: <span className="font-bold text-blue-600">{item.suggested_order_qty}</span></p>
                    <p>Reorder Level: <span className="font-bold text-gray-900">{item.reorder_level}</span></p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`text-lg font-bold px-3 py-1 rounded ${
                    item.priority === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                    item.priority === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {item.priority}
                  </span>
                  <Button className="mt-3">Order Now</Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <p className="text-center py-8 text-gray-500">All medicines are well-stocked!</p>
        </Card>
      )}
    </div>
  );
}
