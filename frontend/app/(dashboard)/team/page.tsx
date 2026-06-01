"use client";

export default function TeamPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Team Management</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Team Members</h2>
        <p className="text-gray-600 mb-6">
          Manage team members and their roles.
        </p>
        
        <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
          Invite Member
        </button>
      </div>
    </div>
  );
}
