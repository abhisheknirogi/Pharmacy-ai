'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  // Check authentication
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Fetch data
  const { data: reorderData, isLoading: reorderLoading } = useQuery({
    queryKey: ['reorder_suggestions'],
    queryFn: () => apiClient.getReorderSuggestions(7),
  });

  const { data: revenueData, isLoading: revenueLoading } = useQuery({
    queryKey: ['daily_revenue'],
    queryFn: () => apiClient.getDailyRevenue(30),
  });

  const { data: lowStockData, isLoading: lowStockLoading } = useQuery({
    queryKey: ['low_stock'],
    queryFn: () => apiClient.getLowStockMedicines(),
  });

  if (!isAuthenticated) {
    return <div className="p-4">Redirecting...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Welcome back, {user?.email}</h1>
        <p className="text-gray-600 mt-2">Here's what's happening in your pharmacy today</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="text-center py-4">
            <p className="text-4xl font-bold text-blue-600">42</p>
            <p className="text-gray-600 text-sm mt-2">Medicines</p>
          </div>
        </Card>
        <Card className="bg-gradient-to-br from-red-50 to-red-100">
          <div className="text-center py-4">
            <p className="text-4xl font-bold text-red-600">3</p>
            <p className="text-gray-600 text-sm mt-2">Critical Reorder</p>
          </div>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100">
          <div className="text-center py-4">
            <p className="text-4xl font-bold text-yellow-600">8</p>
            <p className="text-gray-600 text-sm mt-2">Expiring Soon</p>
          </div>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-green-100">
          <div className="text-center py-4">
            <p className="text-2xl font-bold text-green-600">$4,250</p>
            <p className="text-gray-600 text-sm mt-2">Today's Revenue</p>
          </div>
        </Card>
      </div>

      {/* Revenue Chart */}
      <Card title="Revenue Trend (Last 30 Days)" className="mb-8">
        {revenueLoading ? (
          <div className="h-80 flex items-center justify-center">
            <p className="text-gray-500">Loading chart...</p>
          </div>
        ) : revenueData?.data ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#0ea5e9" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : null}
      </Card>

      {/* Critical Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card title=" Critical Reorders" description="Medicines with critically low stock">
          {reorderLoading ? (
            <p>Loading...</p>
          ) : reorderData?.data && reorderData.data.length > 0 ? (
            <ul className="space-y-3">
              {reorderData.data.slice(0, 5).map((item: any) => (
                <li key={item.medicine_id} className="flex justify-between p-3 bg-red-50 rounded border border-red-200">
                  <div>
                    <p className="font-semibold text-gray-900">{item.medicine_name}</p>
                    <p className="text-sm text-gray-600">Stock: {item.current_stock} / Recommended: {item.suggested_order_qty}</p>
                  </div>
                  <span className="text-red-600 font-bold text-lg">{item.priority}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600">All medicines are well-stocked!</p>
          )}
        </Card>

        <Card title=" Quick Links">
          <div className="space-y-3">
            <a href="/inventory" className="block p-3 rounded border border-gray-200 hover:bg-blue-50 transition-colors">
              <p className="font-semibold text-blue-600">Manage Inventory</p>
              <p className="text-sm text-gray-600">Add, edit, or remove medicines</p>
            </a>
            <a href="/sales" className="block p-3 rounded border border-gray-200 hover:bg-blue-50 transition-colors">
              <p className="font-semibold text-blue-600">Record Sales</p>
              <p className="text-sm text-gray-600">Track daily transactions</p>
            </a>
            <a href="/reorder" className="block p-3 rounded border border-gray-200 hover:bg-blue-50 transition-colors">
              <p className="font-semibold text-blue-600">AI Reorder</p>
              <p className="text-sm text-gray-600">Get AI-powered predictions</p>
            </a>
          </div>
        </Card>
      </div>
    </div>
  );
}
