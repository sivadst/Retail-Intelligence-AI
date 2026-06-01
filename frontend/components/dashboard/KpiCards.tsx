"use client";

import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, 
         Package, Percent, Users, BarChart3 } from "lucide-react";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils";

interface KpiData {
  total_sales: number;
  total_profit: number;
  profit_margin: number;
  total_orders: number;
  avg_order_value: number;
  growth_pct: number;
  period_start: string;
  period_end: string;
}

const kpiConfig = [
  { key: "total_sales", label: "Total Sales", icon: DollarSign, format: formatCurrency },
  { key: "total_profit", label: "Total Profit", icon: TrendingUp, format: formatCurrency },
  { key: "profit_margin", label: "Profit Margin", icon: Percent, format: formatPercent },
  { key: "total_orders", label: "Total Orders", icon: ShoppingCart, format: formatNumber },
  { key: "avg_order_value", label: "Avg Order Value", icon: Package, format: formatCurrency },
  { key: "growth_pct", label: "Growth", icon: BarChart3, format: formatPercent },
];

export default function KpiCards({ data }: { data?: KpiData }) {
  if (!data) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {kpiConfig.map((kpi) => {
        const value = data[kpi.key as keyof KpiData];
        const isGrowth = kpi.key === "growth_pct";
        const isPositive = isGrowth ? (value as number) >= 0 : (value as number) >= 0;
        
        return (
          <div key={kpi.key} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-500 text-sm font-medium">{kpi.label}</span>
              <div className={`p-2 rounded-lg ${isPositive ? 'bg-emerald-50' : 'bg-rose-50'}`}>
                <kpi.icon className={`w-4 h-4 ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`} />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {kpi.format(value as number)}
            </div>
            {isGrowth && (
              <div className={`flex items-center gap-1 mt-2 text-sm font-medium ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
                {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {Math.abs(value as number).toFixed(1)}% vs last period
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}