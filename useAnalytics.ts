import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useKpis(datasetId: string | null, dateRangeLabel: string) {
  return useQuery({
    queryKey: ['analytics', 'kpis', datasetId, dateRangeLabel],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/kpis', {
        params: { dataset_id: datasetId, date_range: dateRangeLabel }
      });
      return response.data;
    },
    enabled: !!datasetId,
  });
}

export function useSalesTrend(datasetId: string | null, dateRangeLabel: string, granularity: string = 'daily') {
  return useQuery({
    queryKey: ['analytics', 'sales-trend', datasetId, dateRangeLabel, granularity],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/sales-trend', {
        params: { dataset_id: datasetId, date_range: dateRangeLabel, granularity }
      });
      return response.data;
    },
    enabled: !!datasetId,
  });
}

export function useCategoryBreakdown(datasetId: string | null, metric: string = 'sales') {
  return useQuery({
    queryKey: ['analytics', 'category-breakdown', datasetId, metric],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/category-breakdown', {
        params: { dataset_id: datasetId, metric }
      });
      return response.data;
    },
    enabled: !!datasetId,
  });
}