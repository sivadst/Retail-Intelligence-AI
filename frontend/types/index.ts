"""Frontend TypeScript types."""

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "owner" | "admin" | "analyst" | "viewer";
  organization_id: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export interface Organization {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Dataset {
  id: string;
  name: string;
  description?: string;
  organization_id: string;
  file_size: number;
  file_type: string;
  row_count?: number;
  column_count?: number;
  processing_status: "pending" | "processing" | "completed" | "failed";
  processing_error?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  message_type: "user" | "assistant" | "system";
  content: string;
  sql_query?: string;
  chart_type?: string;
  created_at: string;
}

export interface Alert {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  condition: Record<string, unknown>;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface KPIs {
  total_sales: number;
  total_profit: number;
  profit_margin: number;
  total_orders: number;
  average_order_value: number;
  top_category: string;
  growth_percent: number;
}
