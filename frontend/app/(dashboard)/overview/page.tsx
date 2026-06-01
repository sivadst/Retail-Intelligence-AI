"use client";

import { useAppStore } from "@/stores/app";
import { useKpis, useSalesTrend, useCategoryBreakdown } from "@/hooks/useAnalytics";
import { useDatasets } from "@/hooks/useDatasets";
import DatasetSelector from "@/components/shared/DatasetSelector";
import DateRangePicker from "@/components/shared/DateRangePicker";
import { CardSkeleton, Skeleton } from "@/components/shared/LoadingSkeleton";
import EmptyState from "@/components/shared/EmptyState";
import KpiCards from "@/components/dashboard/KpiCards";
import SalesTrendChart from "@/components/dashboard/SalesTrendChart";
import CategoryBreakdown from "@/components/dashboard/CategoryBreakdown";
import RecentActivity from "@/components/dashboard/RecentActivity";
import { BarChart3, TrendingUp, AlertCircle } from "lucide-react";
import Link from "next/link";

export default function OverviewPage() {
  const { selectedDatasetId, dateRange } = useAppStore();
  const { data: datasets } = useDatasets();
  
  const kpisQuery = useKpis(selectedDatasetId, dateRange.label);
  const trendQuery = useSalesTrend(selectedDatasetId, dateRange.label, "daily");
  const categoryQuery = useCategoryBreakdown(selectedDatasetId, "sales");

  const hasDatasets = datasets && datasets.length > 0;

  if (!hasDatasets) {
    return (
      <div className="p-8">
        <EmptyState
          title="No datasets yet"
          description="Upload your first retail dataset to start analyzing your business performance."
          icon={<BarChart3 className="w-8 h-8" />}
          action={
            <Link href="/datasets/upload" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
              Upload Dataset
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard Overview</h1>
          <p className="text-slate-500 text-sm mt-1">
            Real-time insights into your retail performance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <DatasetSelector />
          <DateRangePicker />
        </div>
      </div>

      {/* KPI Cards */}
      {kpisQuery.isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : kpisQuery.error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-sm">
          <AlertCircle className="w-4 h-4 inline mr-2" />
          Failed to load KPIs. Please try again.
        </div>
      ) : (
        <KpiCards data={kpisQuery.data?.data} />
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales Trend - takes 2/3 width */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Sales Trend
            </h2>
          </div>
          {trendQuery.isLoading ? (
            <Skeleton className="h-80 w-full" />
          ) : trendQuery.error ? (
            <EmptyState title="No trend data" description="Upload a dataset with date and sales columns." />
          ) : (
            <SalesTrendChart data={trendQuery.data?.data} />
          )}
        </div>

        {/* Category Breakdown - takes 1/3 width */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Sales by Category</h2>
          {categoryQuery.isLoading ? (
            <Skeleton className="h-80 w-full" />
          ) : categoryQuery.error ? (
            <EmptyState title="No category data" description="Upload a dataset with category column." />
          ) : (
            <CategoryBreakdown data={categoryQuery.data?.data} />
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <RecentActivity />
    </div>
  );
}
