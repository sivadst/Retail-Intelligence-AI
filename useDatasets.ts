import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface Dataset {
  id: string;
  name: string;
  file_size?: number;
  file_type?: string;
  row_count: number;
  column_count: number;
  processing_status: string;
  created_at: string;
}

export function useDatasets() {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      const response = await api.get<Dataset[]>('/datasets');
      return response.data;
    },
  });
}