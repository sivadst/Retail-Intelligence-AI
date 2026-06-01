"use client";
import { useState } from "react";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { ArrowUpDown } from "lucide-react";

interface ProductData {
  product_name: string;
  category: string;
  sales: number;
  profit: number;
  margin: number;
}

export default function TopProductsTable({ data }: { data?: ProductData[] }) {
  const [sortConfig, setSortConfig] = useState<{ key: keyof ProductData; direction: 'asc' | 'desc' } | null>(null);
  
  if (!data) return null;
  
  const sorted = [...data].sort((a, b) => {
    if (!sortConfig) return 0;
    const aVal = a[sortConfig.key];
    const bVal = b[sortConfig.key];
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
    }
    return 0;
  });

  const requestSort = (key: keyof ProductData) => {
    setSortConfig(current => ({
      key,
      direction: current?.key === key && current.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            {[
              { key: 'product_name', label: 'Product' },
              { key: 'category', label: 'Category' },
              { key: 'sales', label: 'Sales' },
              { key: 'profit', label: 'Profit' },
              { key: 'margin', label: 'Margin' },
            ].map((col) => (
              <th 
                key={col.key}
                onClick={() => requestSort(col.key as keyof ProductData)}
                className="text-left py-3 px-4 font-medium text-slate-700 cursor-pointer hover:bg-slate-100"
              >
                <div className="flex items-center gap-1">
                  {col.label}
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((product, i) => (
            <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
              <td className="py-3 px-4 font-medium text-slate-900">{product.product_name}</td>
              <td className="py-3 px-4 text-slate-600">{product.category}</td>
              <td className="py-3 px-4 text-slate-900">{formatCurrency(product.sales)}</td>
              <td className="py-3 px-4 text-slate-900">{formatCurrency(product.profit)}</td>
              <td className="py-3 px-4">
                <span className={`${product.margin >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {formatPercent(product.margin)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}