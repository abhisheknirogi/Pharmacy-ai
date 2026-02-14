import type { Metadata } from 'next';
import './globals.css';
import Header from '@/components/layout/header';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'PharmaRec AI - Pharmacy Management',
  description: 'AI-powered pharmacy inventory, sales, and reorder prediction system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <Providers>
          <Header />
          <main className="min-h-screen">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
