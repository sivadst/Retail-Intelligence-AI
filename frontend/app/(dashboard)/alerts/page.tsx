"use client";

export default function AlertsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Alerts</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Smart Alerts</h2>
        <p className="text-gray-600 mb-6">
          Set up custom alert rules to monitor key metrics in real-time.
        </p>
        
        <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
          Create New Alert
        </button>
      </div>
    </div>
  );
}
