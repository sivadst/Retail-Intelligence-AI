"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/stores/app";
import DatasetSelector from "@/components/shared/DatasetSelector";
import { CardSkeleton } from "@/components/shared/LoadingSkeleton";
import EmptyState from "@/components/shared/EmptyState";
import { TrendingUp, BarChart3, Loader2, Download } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface ForecastPoint {
  ds: string;
  y?: number;
  yhat?: number;
  yhat_lower?: number;
  yhat_upper?: number;
}

export default function ForecastingPage() {
  const { selectedDatasetId } = useAppStore();
  const [metric, setMetric] = useState<"sales" | "profit" | "orders">("sales");
  const [granularity, setGranularity] = useState<"daily" | "weekly" | "monthly">("daily");
  const [horizon, setHorizon] = useState(30);

  const forecastMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post("/api/v1/forecasting/forecast", {
        dataset_id: selectedDatasetId,
        metric,
        granularity,
        horizon,
      });
      return res.data?.data;
    },
  });

  const forecast = forecastMutation.data;
  const chartData: ForecastPoint[] = forecast 
    ? [...(forecast.historical || []), ...(forecast.forecast || [])]
    : [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Demand Forecasting</h1>
          <p className="text-slate-500 text-sm mt-1">
            Predict future trends using AI-powered time series analysis
          </p>
        </div>
        <DatasetSelector />
      </div>

      {/* Controls */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Metric</label>
            <div className="flex bg-slate-100 rounded-lg p-1">
              {(["sales", "profit", "orders"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMetric(m)}
                  className={`flex-1 py-2 text-sm font-medium rounded-md capitalize transition-colors ${
                    metric === m ? "bg-white text-blue-600 shadow-sm" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Granularity</label>
            <div className="flex bg-slate-100 rounded-lg p-1">
              {(["daily", "weekly", "monthly"] as const).map((g) => (
                <button
                  key={g}
                  onClick={() => setGranularity(g)}
                  className={`flex-1 py-2 text-sm font-medium rounded-md capitalize transition-colors ${
                    granularity === g ? "bg-white text-blue-600 shadow-sm" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Horizon: <span className="text-blue-600">{horizon} days</span>
            </label>
            <input
              type="range"
              min={30}
              max={90}
              step={30}
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>30d</span>
              <span>60d</span>
              <span>90d</span>
            </div>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => forecastMutation.mutate()}
              disabled={!selectedDatasetId || forecastMutation.isPending}
              className="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {forecastMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Training Model...
                </>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4" />
                  Generate Forecast
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {forecastMutation.isPending && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {forecastMutation.error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-sm">
          Failed to generate forecast. Ensure your dataset has enough historical data (60+ days).
        </div>
      )}

      {forecast && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="text-sm text-slate-500 mb-1">Predicted Total</div>
              <div className="text-2xl font-bold text-slate-900">
                ${forecast.metrics?.predicted_total?.toLocaleString() || "—"}
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="text-sm text-slate-500 mb-1">Trend Direction</div>
              <div className={`text-2xl font-bold ${forecast.metrics?.trend_direction === "upward" ? "text-emerald-600" : "text-rose-600"}`}>
                {forecast.metrics?.trend_direction === "upward" ? "↗ Upward" : "↘ Downward"}
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="text-sm text-slate-500 mb-1">Model Accuracy (MAPE)</div>
              <div className="text-2xl font-bold text-slate-900">
                {forecast.metrics?.mape?.toFixed(1) || "—"}%
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="text-sm text-slate-500 mb-1">Peak Season</div>
              <div className="text-2xl font-bold text-slate-900">
                {forecast.metrics?.peak_season || "—"}
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                Forecast Chart
              </h2>
              <button className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
                <Download className="w-4 h-4" /> Export
              </button>
            </div>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="ds" 
                  tickFormatter={(v) => new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                />
                <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip 
                  labelFormatter={(v) => new Date(v).toLocaleDateString()}
                  formatter={(value: number, name: string) => [
                    name === "y" ? `Actual: $${value.toLocaleString()}` : `Forecast: $${value.toLocaleString()}`,
                    ""
                  ]}
                />
                <Area type="monotone" dataKey="y" stroke="#2563eb" fill="none" strokeWidth={2} name="Historical" />
                <Area type="monotone" dataKey="yhat" stroke="#10b981" fill="url(#forecastGradient)" strokeWidth={2} strokeDasharray="5 5" name="Forecast" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}