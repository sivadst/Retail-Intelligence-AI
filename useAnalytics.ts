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

export function useRegionalPerformance(datasetId: string | null, metric: string = 'sales') {
  return useQuery({
    queryKey: ['analytics', 'regional-performance', datasetId, metric],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/regional-performance', {
        params: { dataset_id: datasetId, metric }
      });
      return response.data;
    },
    enabled: !!datasetId,
  });
}

export function useTopProducts(datasetId: string | null, limit: number = 10, sortBy: string = 'sales') {
  return useQuery({
    queryKey: ['analytics', 'top-products', datasetId, limit, sortBy],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/top-products', {
        params: { dataset_id: datasetId, limit, sort_by: sortBy }
      });
      return response.data;
    },
    enabled: !!datasetId,
  });
}

export function useDiscountAnalysis(datasetId: string | null) {
  return useQuery({
    queryKey: ['analytics', 'discount-analysis', datasetId],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/discount-analysis', {
        params: { dataset_id: datasetId }
      });
      return response.data;
    },
    enabled: !!datasetId,
  });
}