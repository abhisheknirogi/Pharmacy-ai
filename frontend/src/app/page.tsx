'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth-store';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

/**
 * Feature item type definition
 */
interface FeatureItem {
  id: string;
  title: string;
  description: string;
  icon: string;
}

const FEATURES: FeatureItem[] = [
  {
    id: 'inventory',
    title: 'Inventory Management',
    description: 'Track medicines, batches, expiry dates, and stock levels in real-time',
    icon: '📦',
  },
  {
    id: 'sales',
    title: 'Sales Tracking',
    description: 'Record transactions, generate bills, and analyze revenue trends',
    icon: '💰',
  },
  {
    id: 'ai-reorders',
    title: 'AI Reorders',
    description: 'Get intelligent reorder suggestions based on sales patterns and demand forecasting',
    icon: '🤖',
  },
  {
    id: 'expiry-alerts',
    title: 'Expiry Alerts',
    description: 'Never miss expiry dates with automated alerts and reports',
    icon: '⏰',
  },
  {
    id: 'analytics',
    title: 'Analytics',
    description: 'Visualize data with comprehensive dashboards and insights',
    icon: '📊',
  },
  {
    id: 'performance',
    title: 'Fast & Reliable',
    description: 'Built with modern tech stack for performance and reliability',
    icon: '⚡',
  },
];

/**
 * Hero section component
 */
const HeroSection: React.FC<{ isAuthenticated: boolean }> = ({ isAuthenticated }) => (
  <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
    <div className="max-w-7xl mx-auto px-4 py-20 text-center">
      <h1 className="text-5xl font-bold mb-4">PharmaRec AI</h1>
      <p className="text-xl mb-8 text-blue-100">
        AI-Powered Pharmacy Inventory Management & Reorder Prediction System
      </p>
      {!isAuthenticated && (
        <div className="flex gap-4 justify-center flex-wrap">
          <Link href="/login">
            <Button variant="secondary" size="lg" aria-label="Sign in to your account">
              Sign In
            </Button>
          </Link>
          <Link href="/register">
            <Button size="lg" aria-label="Create a new account">
              Get Started
            </Button>
          </Link>
        </div>
      )}
    </div>
  </section>
);

/**
 * Feature card component
 */
const FeatureCard: React.FC<{ feature: FeatureItem }> = ({ feature }) => (
  <Card className="hover:shadow-lg transition-shadow duration-300">
    <div className="text-center p-6">
      <div className="text-4xl mb-4" role="img" aria-label={feature.title}>{feature.icon}</div>
      <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
      <p className="text-gray-600">{feature.description}</p>
    </div>
  </Card>
);

/**
 * Features section component
 */
const FeaturesSection: React.FC = () => (
  <section className="max-w-7xl mx-auto px-4 py-16">
    <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {FEATURES.map((feature) => (
        <FeatureCard key={feature.id} feature={feature} />
      ))}
    </div>
  </section>
);

/**
 * Call-to-action section component
 */
const CTASection: React.FC<{ isAuthenticated: boolean }> = ({ isAuthenticated }) => {
  if (isAuthenticated) return null;

  return (
    <section className="bg-blue-50 py-16">
      <div className="max-w-4xl mx-auto text-center px-4">
        <h2 className="text-3xl font-bold mb-4">Ready to streamline your pharmacy?</h2>
        <p className="text-gray-600 mb-8">
          Start using PharmaRec AI today to optimize inventory and boost sales
        </p>
        <Link href="/register">
          <Button size="lg" aria-label="Create free account">
            Create Free Account
          </Button>
        </Link>
      </div>
    </section>
  );
};

/**
 * Footer component
 */
const Footer: React.FC = () => (
  <footer className="bg-gray-900 text-white py-8">
    <div className="max-w-7xl mx-auto px-4 text-center">
      <p>© 2024 PharmaRec AI - Pharmacy Management Made Easy</p>
      <p className="text-gray-400 mt-2">Open-source AI-powered solution for modern pharmacies</p>
    </div>
  </footer>
);

/**
 * Home page component
 */
export default function HomePage(): React.ReactElement {
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState<boolean>(false);

  // Handle hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-pulse" role="status" aria-live="polite">
          <div className="h-12 bg-gray-300 rounded w-32"></div>
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <HeroSection isAuthenticated={isAuthenticated} />
      <FeaturesSection />
      <CTASection isAuthenticated={isAuthenticated} />
      <Footer />
    </div>
  );
}
