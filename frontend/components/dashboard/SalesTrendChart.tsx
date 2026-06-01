"use client";

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatCurrency } from "@/lib/utils";

interface TrendPoint {
  date: string;
  sales: number;
  profit: number;
  orders: number;
}

export default function SalesTrendChart({ data }: { data?: TrendPoint[] }) {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12, fill: "#64748b" }}
          tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        />
        <YAxis 
          tick={{ fontSize: 12, fill: "#64748b" }}
          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '1px solid #e2e8f0', 
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
          }}
          formatter={(value: number) => [formatCurrency(value), ""]}
          labelFormatter={(label) => new Date(label).toLocaleDateString()}
        />
        <Area 
          type="monotone" 
          dataKey="sales" 
          stroke="#2563eb" 
          strokeWidth={2}
          fill="url(#salesGradient)" 
        />
        <Area 
          type="monotone" 
          dataKey="profit" 
          stroke="#10b981" 
          strokeWidth={2}
          fill="none" 
          strokeDasharray="5 5"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}