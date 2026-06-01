"use client";

import { useEffect } from 'react';
import { useDatasets } from '@/hooks/useDatasets';
import { useAppStore } from '@/stores/app';
import { Database, Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function DatasetSelector() {
  const { data: datasets, isLoading, error } = useDatasets();
  const { selectedDatasetId, setSelectedDatasetId } = useAppStore();
  const router = useRouter();

  useEffect(() => {
    if (datasets && datasets.length > 0 && !selectedDatasetId) {
      // Auto-select the first completed dataset
      const completed = datasets.find(d => d.processing_status === 'completed');
      if (completed) {
        setSelectedDatasetId(completed.id);
      } else {
        setSelectedDatasetId(datasets[0].id);
      }
    }
  }, [datasets, selectedDatasetId, setSelectedDatasetId]);

  if (isLoading) {
    return (
      <div className="animate-pulse bg-slate-200 h-10 w-64 rounded-md"></div>
    );
  }

  if (error) {
    return (
      <div className="text-rose-500 text-sm flex items-center h-10">
        Error loading datasets
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <select
          value={selectedDatasetId || ''}
          onChange={(e) => setSelectedDatasetId(e.target.value)}
          className="appearance-none bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-64 pl-10 p-2.5 shadow-sm truncate"
        >
          <option value="" disabled>Select a dataset...</option>
          {datasets?.map((dataset) => (
            <option key={dataset.id} value={dataset.id}>
              {dataset.name} ({dataset.row_count?.toLocaleString() || 0} rows)
            </option>
          ))}
        </select>
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <Database className="w-4 h-4 text-slate-500" />
        </div>
      </div>
      <button
        onClick={() => router.push('/overview')}
        className="p-2.5 text-slate-500 bg-slate-50 border border-slate-300 rounded-lg hover:bg-slate-100 hover:text-blue-600 transition-colors shadow-sm"
        title="Upload New Dataset"
      >
        <Plus className="w-4 h-4" />
      </button>
    </div>
  );
}