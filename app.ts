import { create } from 'zustand';

interface DateRange {
  start: string;
  end: string;
  label: string;
}

interface Filters {
  categories: string[];
  regions: string[];
  metric: 'sales' | 'profit' | 'quantity' | 'orders';
}

interface AppState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  selectedDatasetId: string | null;
  dateRange: DateRange;
  filters: Filters;
  
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setSelectedDatasetId: (id: string | null) => void;
  setDateRange: (range: DateRange) => void;
  setFilters: (filters: Partial<Filters>) => void;
  resetFilters: () => void;
}

const defaultDateRange = {
  start: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString(),
  end: new Date().toISOString(),
  label: 'last_30d',
};

const defaultFilters: Filters = {
  categories: [],
  regions: [],
  metric: 'sales',
};

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  theme: 'light',
  selectedDatasetId: null,
  dateRange: defaultDateRange,
  filters: defaultFilters,
  
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => set({ theme }),
  setSelectedDatasetId: (id) => set({ selectedDatasetId: id }),
  setDateRange: (range) => set({ dateRange: range }),
  setFilters: (filters) => set((state) => ({ filters: { ...state.filters, ...filters } })),
  resetFilters: () => set({ filters: defaultFilters }),
}));