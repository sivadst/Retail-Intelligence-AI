"use client";

import Link from "next/link";
import { ArrowRight, BarChart3, Brain, Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="p-6 border-b border-gray-200 bg-white/50 backdrop-blur">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Retail Intelligence AI</h1>
          <div className="space-x-4">
            <Link
              href="/login"
              className="text-gray-700 hover:text-gray-900 font-medium"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 py-24 text-center">
        <h2 className="text-5xl font-bold text-gray-900 mb-6">
          AI-Powered Retail Analytics
        </h2>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Make data-driven decisions with real-time insights, predictive forecasting, and
          intelligent recommendations powered by advanced AI.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            href="/register"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition font-medium inline-flex items-center"
          >
            Start Free Trial <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
          <Link
            href="/login"
            className="border border-gray-300 text-gray-900 px-8 py-3 rounded-lg hover:bg-gray-50 transition font-medium"
          >
            Sign In
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h3 className="text-3xl font-bold text-gray-900 mb-12 text-center">
          Powerful Features
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            icon={BarChart3}
            title="Real-time Analytics"
            description="Monitor KPIs and metrics with live dashboards and interactive charts"
          />
          <FeatureCard
            icon={Brain}
            title="AI Assistant"
            description="Ask questions about your data and get instant insights in natural language"
          />
          <FeatureCard
            icon={Zap}
            title="Predictive Forecasting"
            description="Forecast sales, demand, and trends using advanced time-series models"
          />
        </div>
      </section>

      {/* CTA */}
      <section className="bg-blue-600 text-white py-16">
        <div className="max-w-2xl mx-auto text-center px-6">
          <h3 className="text-3xl font-bold mb-4">Ready to transform your retail business?</h3>
          <p className="mb-8 text-blue-100">
            Join leading retailers using Retail Intelligence AI to grow their business
          </p>
          <Link
            href="/register"
            className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:bg-blue-50 transition font-medium"
          >
            Start Free Trial
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <p>&copy; 2024 Retail Intelligence AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ComponentType<{ className: string }>;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-8 hover:shadow-lg transition">
      <Icon className="w-12 h-12 text-blue-600 mb-4" />
      <h4 className="text-xl font-semibold text-gray-900 mb-2">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
