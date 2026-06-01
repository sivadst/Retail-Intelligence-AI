"use client";

export default function ReportsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Reports</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Reports</h2>
        <p className="text-gray-600 mb-6">
          Create and schedule custom reports with your analytics data.
        </p>
        
        <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
          New Report
        </button>
      </div>
    </div>
  );
}
