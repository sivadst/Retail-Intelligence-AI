"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { MessageSquare, Database, Clock, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function RecentActivity() {
  const { data: conversations } = useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const res = await api.get('/api/v1/ai/conversations');
      return res.data?.data || [];
    },
  });

  const recentChats = conversations?.slice(0, 3) || [];

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-900">Recent Activity</h2>
        <Link href="/ai-assistant" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
          View all <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
      
      {recentChats.length === 0 ? (
        <p className="text-slate-500 text-sm">No recent AI conversations. Try asking a question!</p>
      ) : (
        <div className="space-y-3">
          {recentChats.map((chat: any) => (
            <div key={chat.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="p-2 bg-blue-50 rounded-lg">
                <MessageSquare className="w-4 h-4 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {chat.messages?.[0]?.content || "New conversation"}
                </p>
                <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                  <Clock className="w-3 h-3" />
                  {new Date(chat.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}