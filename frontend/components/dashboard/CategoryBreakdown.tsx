"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

interface CategoryData {
  category: string;
  value: number;
  pct: number;
}

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'];

export default function CategoryBreakdown({ data }: { data?: CategoryData[] }) {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
          nameKey="category"
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip 
          formatter={(value: number, name: string, props: any) => [
            `$${value.toLocaleString()} (${props?.payload?.pct?.toFixed(1)}%)`,
            name
          ]}
        />
        <Legend 
          verticalAlign="bottom" 
          height={36}
          formatter={(value: string, entry: any) => (
            <span className="text-slate-600 text-sm">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}