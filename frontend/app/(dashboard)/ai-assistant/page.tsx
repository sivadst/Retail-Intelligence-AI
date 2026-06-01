"use client";

import { useState, useRef, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/stores/app";
import DatasetSelector from "@/components/shared/DatasetSelector";
import { Send, Loader2, Bot, User, Database, BarChart3, Table, Code } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sqlQuery?: string;
  chartData?: any[];
  chartType?: string;
  chartTitle?: string;
}

export default function AIAssistantPage() {
  const { selectedDatasetId } = useAppStore();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: suggestedQuestions } = useQuery({
    queryKey: ['suggested-questions', selectedDatasetId],
    queryFn: async () => {
      if (!selectedDatasetId) return [];
      const res = await api.get(`/api/v1/ai/suggested-questions?dataset_id=${selectedDatasetId}`);
      return res.data?.data || [];
    },
    enabled: !!selectedDatasetId,
  });

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const res = await api.post('/api/v1/ai/chat', {
        message,
        dataset_id: selectedDatasetId,
      });
      return res.data?.data;
    },
    onMutate: async (message) => {
      const userMsg: Message = {
        id: Date.now().toString(),
        role: "user",
        content: message,
      };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");
    },
    onSuccess: (data) => {
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message,
        sqlQuery: data.sql_query,
        chartData: data.results,
        chartType: data.chart_type,
        chartTitle: data.chart_title,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedDatasetId || chatMutation.isPending) return;
    chatMutation.mutate(input.trim());
  };

  const handleSuggestedQuestion = (question: string) => {
    if (!selectedDatasetId || chatMutation.isPending) return;
    chatMutation.mutate(question);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">AI Analytics Assistant</h1>
          <p className="text-sm text-slate-500">Ask questions about your data in natural language</p>
        </div>
        <DatasetSelector />
      </div>

      {!selectedDatasetId ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Database className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900">Select a dataset</h3>
            <p className="text-slate-500 mt-1">Choose a dataset to start asking questions</p>
          </div>
        </div>
      ) : (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
            {messages.length === 0 && (
              <div className="text-center py-12">
                <Bot className="w-12 h-12 text-blue-200 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  Hi! I'm your Retail AI Assistant
                </h3>
                <p className="text-slate-500 mb-6 max-w-md mx-auto">
                  Ask me anything about your retail data. I can analyze trends, find insights, 
                  and generate charts from your data.
                </p>
                
                {suggestedQuestions && suggestedQuestions.length > 0 && (
                  <div className="flex flex-wrap justify-center gap-2 max-w-2xl mx-auto">
                    {suggestedQuestions.map((q: string, i: number) => (
                      <button
                        key={i}
                        onClick={() => handleSuggestedQuestion(q)}
                        className="px-4 py-2 bg-slate-50 border border-slate-200 rounded-full text-sm text-slate-700 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-colors"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-blue-600" />
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white border border-slate-200 text-slate-900 shadow-sm"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <p>{msg.content}</p>
                  )}

                  {/* Chart/Data Table */}
                  {msg.chartData && msg.chartData.length > 0 && msg.role === "assistant" && (
                    <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="flex items-center gap-2 mb-2">
                        {msg.chartType === 'table' ? (
                          <Table className="w-4 h-4 text-slate-500" />
                        ) : (
                          <BarChart3 className="w-4 h-4 text-slate-500" />
                        )}
                        <span className="text-xs font-medium text-slate-500 uppercase">
                          {msg.chartType || 'Data'}
                        </span>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-200">
                              {Object.keys(msg.chartData[0]).map((key) => (
                                <th key={key} className="text-left py-2 px-3 font-medium text-slate-700">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {msg.chartData.slice(0, 10).map((row: any, i: number) => (
                              <tr key={i} className="border-b border-slate-100">
                                {Object.values(row).map((val: any, j: number) => (
                                  <td key={j} className="py-2 px-3 text-slate-600">
                                    {typeof val === 'number' ? val.toLocaleString() : String(val)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* SQL Query (collapsible) */}
                  {msg.sqlQuery && msg.role === "assistant" && (
                    <details className="mt-3">
                      <summary className="text-xs text-slate-500 cursor-pointer flex items-center gap-1">
                        <Code className="w-3 h-3" /> SQL Query
                      </summary>
                      <pre className="mt-2 p-3 bg-slate-900 text-slate-300 rounded-lg text-xs overflow-x-auto">
                        <code>{msg.sqlQuery}</code>
                      </pre>
                    </details>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-slate-600" />
                  </div>
                )}
              </div>
            ))}

            {chatMutation.isPending && (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-blue-600" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl px-5 py-3 shadow-sm">
                  <div className="flex items-center gap-2 text-slate-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Analyzing your data...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-200 bg-white px-6 py-4">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your data..."
                className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                disabled={!input.trim() || chatMutation.isPending || !selectedDatasetId}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </>
      )}
    </div>
  );
}
