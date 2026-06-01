"use client";

export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Organization</h2>
          <p className="text-gray-600">Manage your organization settings and preferences</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Integration</h2>
          <p className="text-gray-600">Connect external services and manage API keys</p>
        </div>
      </div>
    </div>
  );
}
