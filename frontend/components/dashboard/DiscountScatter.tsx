"use client";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { formatCurrency, formatPercent } from "@/lib/utils";

interface DiscountPoint {
  discount: number;
  profit: number;
  sales: number;
}

export default function DiscountScatter({ data, correlation }: { data?: DiscountPoint[]; correlation?: number }) {
  if (!data || data.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis 
          type="number" 
          dataKey="discount" 
          name="Discount" 
          tickFormatter={(v) => formatPercent(v * 100)}
          tick={{ fontSize: 12, fill: "#64748b" }}
        />
        <YAxis 
          type="number" 
          dataKey="profit" 
          name="Profit" 
          tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`}
          tick={{ fontSize: 12, fill: "#64748b" }}
        />
        <Tooltip 
          formatter={(value: number, name: string) => [
            name === 'discount' ? formatPercent(value * 100) : formatCurrency(value),
            name
          ]}
        />
        <ReferenceLine y={0} stroke="#ef4444" strokeDasharray="3 3" />
        <Scatter data={data} fill="#2563eb" />
      </ScatterChart>
    </ResponsiveContainer>
  );
}