"use client";

import { useState, useRef, useEffect } from 'react';
import { useAppStore } from '@/stores/app';
import { Calendar } from 'lucide-react';

export default function DateRangePicker() {
  const { dateRange, setDateRange } = useAppStore();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const presets = [
    { label: 'last_7d', display: 'Last 7 Days', days: 7 },
    { label: 'last_30d', display: 'Last 30 Days', days: 30 },
    { label: 'last_90d', display: 'Last 90 Days', days: 90 },
    { label: 'last_year', display: 'This Year', days: 365 },
    { label: 'all', display: 'All Time', days: 0 },
  ];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelectPreset = (preset: typeof presets[0]) => {
    const end = new Date();
    const start = new Date();
    
    if (preset.days > 0) {
      start.setDate(end.getDate() - preset.days);
    } else {
      start.setFullYear(2000); // arbitrarily far back for "all time"
    }

    setDateRange({
      start: start.toISOString(),
      end: end.toISOString(),
      label: preset.label,
    });
    setIsOpen(false);
  };

  const currentDisplay = presets.find(p => p.label === dateRange.label)?.display || 'Custom Range';

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg px-4 py-2.5 hover:bg-slate-100 shadow-sm transition-colors"
      >
        <Calendar className="w-4 h-4 text-slate-500" />
        <span>{currentDisplay}</span>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 right-0 w-48 bg-white border border-slate-200 rounded-lg shadow-lg z-50 py-1">
          {presets.map((preset) => (
            <button
              key={preset.label}
              onClick={() => handleSelectPreset(preset)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-blue-50 transition-colors ${
                dateRange.label === preset.label ? 'text-blue-600 font-medium bg-blue-50' : 'text-slate-700'
              }`}
            >
              {preset.display}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}