"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/stores/app";
import DatasetSelector from "@/components/shared/DatasetSelector";
import { Bell, Plus, Trash2, Play, AlertTriangle, CheckCircle, XCircle, Loader2 } from "lucide-react";

interface Alert {
  id: string;
  name: string;
  condition_type: string;
  condition_config: any;
  is_active: boolean;
  last_triggered_at: string | null;
}

export default function AlertsPage() {
  const { selectedDatasetId } = useAppStore();
  const [activeTab, setActiveTab] = useState<"active" | "history">("active");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: alerts, refetch } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await api.get('/api/v1/alerts');
      return res.data?.data || [];
    },
  });

  const { data: history } = useQuery({
    queryKey: ['alert-history'],
    queryFn: async () => {
      const res = await api.get('/api/v1/alerts/history');
      return res.data?.data || [];
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/v1/alerts/${id}`),
    onSuccess: () => refetch(),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) => 
      api.put(`/api/v1/alerts/${id}`, { is_active: active }),
    onSuccess: () => refetch(),
  });

  const evaluateMutation = useMutation({
    mutationFn: (id: string) => api.get(`/api/v1/alerts/evaluate/${id}`),
  });

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Smart Alerts</h1>
          <p className="text-slate-500 text-sm mt-1">
            Monitor your business and get notified when something needs attention
          </p>
        </div>
        <div className="flex items-center gap-3">
          <DatasetSelector />
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus className="w-4 h-4" /> Create Alert
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-6">
          {(["active", "history"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium capitalize border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab} {tab === 'active' ? `(${alerts?.length || 0})` : `(${history?.length || 0})`}
            </button>
          ))}
        </div>
      </div>

      {/* Active Alerts */}
      {activeTab === "active" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {alerts?.map((alert: Alert) => (
            <div key={alert.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Bell className={`w-5 h-5 ${alert.is_active ? 'text-blue-600' : 'text-slate-400'}`} />
                  <h3 className="font-semibold text-slate-900">{alert.name}</h3>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => evaluateMutation.mutate(alert.id)}
                    className="p-1.5 text-slate-400 hover:text-blue-600 rounded-lg hover:bg-blue-50"
                    title="Evaluate now"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(alert.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <p className="text-sm text-slate-500 mb-3">
                {alert.condition_type === 'threshold' && `When ${alert.condition_config.metric} ${alert.condition_config.operator} ${alert.condition_config.value}`}
                {alert.condition_type === 'percent_change' && `When ${alert.condition_config.metric} changes ${alert.condition_config.threshold}% vs ${alert.condition_config.period}`}
                {alert.condition_type === 'anomaly' && 'Automatic anomaly detection'}
              </p>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={alert.is_active}
                    onChange={(e) => toggleMutation.mutate({ id: alert.id, active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                  />
                  <span className="text-sm text-slate-600">{alert.is_active ? 'Active' : 'Inactive'}</span>
                </label>
                {alert.last_triggered_at && (
                  <span className="text-xs text-slate-400">
                    Last triggered: {new Date(alert.last_triggered_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* History */}
      {activeTab === "history" && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-700">Alert</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-700">Triggered Value</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-700">Message</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-700">Time</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {history?.map((item: any) => (
                <tr key={item.id} className="border-t border-slate-100">
                  <td className="py-3 px-4 text-sm text-slate-900">{item.alert?.name || 'Unknown'}</td>
                  <td className="py-3 px-4 text-sm text-slate-600 font-mono">{JSON.stringify(item.triggered_value)}</td>
                  <td className="py-3 px-4 text-sm text-slate-600">{item.message}</td>
                  <td className="py-3 px-4 text-sm text-slate-500">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="py-3 px-4">
                    {item.is_read ? (
                      <span className="inline-flex items-center gap-1 text-xs text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                        <CheckCircle className="w-3 h-3" /> Read
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
                        <AlertTriangle className="w-3 h-3" /> Unread
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
