'use client';

import React from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth-store';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function HomePage() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20 text-center">
          <h1 className="text-5xl font-bold mb-4"> PharmaRec AI</h1>
          <p className="text-xl mb-8 text-blue-100">
            AI-Powered Pharmacy Inventory Management & Reorder Prediction System
          </p>
          {!isAuthenticated && (
            <div className="flex gap-4 justify-center">
              <Link href="/login">
                <Button variant="secondary" size="lg">
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button size="lg">Get Started</Button>
              </Link>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card>
            <div className="text-center">
              <div className="text-4xl mb-4"></div>
              <h3 className="text-xl font-semibold mb-2">Inventory Management</h3>
              <p className="text-gray-600">Track medicines, batches, expiry dates, and stock levels in real-time</p>
            </div>
          </Card>

          <Card>
            <div className="text-center">
              <div className="text-4xl mb-4"></div>
              <h3 className="text-xl font-semibold mb-2">Sales Tracking</h3>
              <p className="text-gray-600">Record transactions, generate bills, and analyze revenue trends</p>
            </div>
          </Card>

          <Card>
            <div className="text-center">
              <div className="text-4xl mb-4"></div>
              <h3 className="text-xl font-semibold mb-2">AI Reorders</h3>
              <p className="text-gray-600">Get intelligent reorder suggestions based on sales patterns and demand forecasting</p>
            </div>
          </Card>

          <Card>
            <div className="text-center">
              <div className="text-4xl mb-4"></div>
              <h3 className="text-xl font-semibold mb-2">Expiry Alerts</h3>
              <p className="text-gray-600">Never miss expiry dates with automated alerts and reports</p>
            </div>
          </Card>

          <Card>
            <div className="text-center">
              <div className="text-4xl mb-4"></div>
              <h3 className="text-xl font-semibold mb-2">Analytics</h3>
              <p className="text-gray-600">Visualize data with comprehensive dashboards and insights</p>
            </div>
          </Card>

          <Card>
            <div className="text-center">
              <div className="text-4xl mb-4"></div>
              <h3 className="text-xl font-semibold mb-2">Fast & Reliable</h3>
              <p className="text-gray-600">Built with modern tech stack for performance and reliability</p>
            </div>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      {!isAuthenticated && (
        <section className="bg-blue-50 py-16">
          <div className="max-w-4xl mx-auto text-center px-4">
            <h2 className="text-3xl font-bold mb-4">Ready to streamline your pharmacy?</h2>
            <p className="text-gray-600 mb-8">Start using PharmaRec AI today to optimize inventory and boost sales</p>
            <Link href="/register">
              <Button size="lg">Create Free Account</Button>
            </Link>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p> PharmaRec AI &copy; 2024 - Pharmacy Management Made Easy</p>
          <p className="text-gray-400 mt-2">Open-source AI-powered solution for modern pharmacies</p>
        </div>
      </footer>
    </div>
  );
}
