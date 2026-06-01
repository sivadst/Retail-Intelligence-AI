"use client";

export default function OverviewPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
        <p className="text-gray-600 mt-2">Welcome to your retail analytics dashboard</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard title="Total Sales" value="$124,500" change="+12.5%" />
        <KPICard title="Total Profit" value="$42,300" change="+8.2%" />
        <KPICard title="Profit Margin" value="34%" change="+2.1%" />
        <KPICard title="Total Orders" value="1,284" change="+5.4%" />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ChartPlaceholder title="Sales Over Time" />
        <ChartPlaceholder title="Sales by Category" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartPlaceholder title="Top Products" />
        <ChartPlaceholder title="Regional Performance" />
      </div>
    </div>
  );
}

function KPICard({ title, value, change }: { title: string; value: string; change: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <p className="text-gray-600 text-sm font-medium">{title}</p>
      <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
      <p className="text-green-600 text-sm mt-2">{change} vs last month</p>
    </div>
  );
}

function ChartPlaceholder({ title }: { title: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="h-64 bg-gray-50 rounded flex items-center justify-center text-gray-500">
        Chart will appear here
      </div>
    </div>
  );
}
