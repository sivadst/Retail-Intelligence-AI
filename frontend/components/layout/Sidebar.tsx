"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  TrendingUp,
  Bot,
  Bell,
  FileText,
  Settings,
  Users,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/stores/auth";

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const menuItems = [
    { href: "/overview", label: "Overview", icon: BarChart3 },
    { href: "/analytics", label: "Analytics", icon: TrendingUp },
    { href: "/forecasting", label: "Forecasting", icon: BarChart3 },
    { href: "/ai-assistant", label: "AI Assistant", icon: Bot },
    { href: "/alerts", label: "Alerts", icon: Bell },
    { href: "/reports", label: "Reports", icon: FileText },
  ];

  if (user?.role === "owner" || user?.role === "admin") {
    menuItems.push(
      { href: "/settings", label: "Settings", icon: Settings },
      { href: "/team", label: "Team", icon: Users }
    );
  }

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">Retail AI</h1>
        <p className="text-xs text-gray-500 mt-1">{user?.organization_id}</p>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center px-4 py-2 rounded-lg transition ${
                isActive
                  ? "bg-blue-50 text-blue-600 font-medium"
                  : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <div className="p-3 rounded-lg bg-gray-50 mb-3">
          <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
          <p className="text-xs text-gray-500 truncate">{user?.email}</p>
        </div>
        <button
          onClick={() => logout()}
          className="w-full flex items-center px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Logout
        </button>
      </div>
    </div>
  );
}
