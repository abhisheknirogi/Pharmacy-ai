'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function SalesPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) router.push('/login');
  }, [isAuthenticated, router]);

  const { data: summary } = useQuery({
    queryKey: ['sales_summary'],
    queryFn: () => apiClient.getSalesSummary(30),
    enabled: !!isAuthenticated,
  });

  if (!isAuthenticated) return <div>Redirecting...</div>;

  const chartData = summary?.data?.map((item: any) => ({
    name: item.medicine_name.substring(0, 10),
    sales: item.total_quantity,
    revenue: item.total_amount,
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-2">Sales Tracking</h1>
      <p className="text-gray-600 mb-8">View sales data and revenue</p>

      <Card className="mb-8">
        {chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sales" fill="#0ea5e9" />
              <Bar dataKey="revenue" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center py-8 text-gray-500">No sales data yet</p>
        )}
      </Card>
    </div>
  );
}
