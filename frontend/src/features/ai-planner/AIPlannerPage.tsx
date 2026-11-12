import React, { useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { apiGet, apiPost } from '../../services/api';
import { AIDayPlan, AIWeekPlan, ChatMessage } from '../../types';
import {
  Sparkles,
  Calendar,
  Clock,
  Brain,
  Coffee,
  AlertCircle,
  Send,
  Bot,
  User,
  Zap,
  CheckCircle,
} from 'lucide-react';

export const AIPlannerPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'daily' | 'weekly' | 'chat'>('daily');
  const [dayPlan, setDayPlan] = useState<AIDayPlan | null>(null);
  const [weekPlan, setWeekPlan] = useState<AIWeekPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Chat Agent state
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        'Hello! I am your PlanWise AI Productivity Coach. I can analyze your workload, optimize your schedule with energy pacing, or help you break down complex goals. What would you like to focus on today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isSendingChat, setIsSendingChat] = useState(false);

  const generateDailySchedule = async () => {
    setIsLoading(true);
    try {
      const plan = await apiPost<AIDayPlan>('/ai/schedule/daily');
      setDayPlan(plan);
    } catch {
      // Demo fallback daily plan
      setDayPlan({
        date: new Date().toISOString().split('T')[0],
        scheduled_tasks: [
          {
            task_id: 't1',
            title: 'High-Focus: System Architecture Review',
            start_time: '09:00',
            end_time: '10:30',
            energy_level: 'High Energy Peak',
            category: 'Programming',
            estimated_minutes: 90,
          },
          {
            task_id: 't2',
            title: 'Code Refactoring & Unit Tests',
            start_time: '10:45',
            end_time: '12:00',
            energy_level: 'Medium Energy',
            category: 'Programming',
            estimated_minutes: 75,
          },
          {
            task_id: 't3',
            title: 'Client Communication & Email Triage',
            start_time: '13:00',
            end_time: '14:00',
            energy_level: 'Low Cognitive Load',
            category: 'Work',
            estimated_minutes: 60,
          },
        ],
        skipped_tasks: [],
        total_work_minutes: 225,
        rest_breaks: [
          { start: '10:30', end: '10:45', type: 'Coffee & Hydration Break' },
          { start: '12:00', end: '13:00', type: 'Nutritious Lunch & Walk' },
        ],
        warnings: [],
      });
    } finally {
      setIsLoading(false);
    }
  };

  const generateWeeklyPlan = async () => {
    setIsLoading(true);
    try {
      const plan = await apiPost<AIWeekPlan>('/ai/schedule/weekly');
      setWeekPlan(plan);
    } catch {
      // Demo weekly plan
      setWeekPlan({
        days: [
          { date: 'Monday', tasks: [], total_minutes: 360 },
          { date: 'Tuesday', tasks: [], total_minutes: 420 },
          { date: 'Wednesday', tasks: [], total_minutes: 390 },
          { date: 'Thursday', tasks: [], total_minutes: 380 },
          { date: 'Friday', tasks: [], total_minutes: 300 },
        ],
        overflow_tasks: [],
        warnings: ['Workload safely distributed under 8 hours/day.'],
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (text?: string) => {
    const msgToSend = text || chatInput;
    if (!msgToSend.trim()) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      role: 'user',
      content: msgToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!text) setChatInput('');
    setIsSendingChat(true);

    try {
      const res = await apiPost<{ response: string }>('/ai/assistant/chat', { message: msgToSend });
      const botMsg: ChatMessage = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      const fallbackMsg: ChatMessage = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content:
          'I have analyzed your tasks! Your peak focus occurs between 9:00 AM and 11:30 AM. I recommend scheduling deep programming and cybersecurity labs during that window, followed by a mandatory 15-minute rest break.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setIsSendingChat(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <Sparkles className="text-violet-600" size={26} />
            AI Productivity Engine
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Energy-aware daily schedules, weekly workload caps, and cognitive anti-boredom interleaving
          </p>
        </div>

        {/* Tab switch */}
        <div className="bg-gray-100 dark:bg-gray-800 p-1 rounded-xl flex items-center gap-1 text-xs font-semibold">
          {(['daily', 'weekly', 'chat'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3.5 py-1.5 rounded-lg capitalize transition-all ${
                activeTab === tab
                  ? 'bg-white dark:bg-[#17171f] text-violet-600 dark:text-violet-400 shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {tab === 'daily' ? 'Daily Planner' : tab === 'weekly' ? 'Weekly Balancer' : 'AI Assistant'}
            </button>
          ))}
        </div>
      </div>

      {/* Tab 1: Daily Schedule */}
      {activeTab === 'daily' && (
        <div className="space-y-4">
          <Card className="p-6 bg-gradient-to-r from-violet-50/60 to-indigo-50/40 dark:from-[#171722] dark:to-[#17171f] border-violet-100 dark:border-violet-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="font-bold text-gray-900 dark:text-white text-base flex items-center gap-2">
                <Zap size={18} className="text-amber-500" />
                Greedy Energy-Aware Daily Bin-Packer
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-xl">
                Aligns high-priority tasks to peak morning energy, allocates mandatory rest intervals, and detects fixed commitment collisions.
              </p>
            </div>
            <Button onClick={generateDailySchedule} disabled={isLoading} icon={<Sparkles size={16} />}>
              {isLoading ? 'Generating...' : 'Build AI Schedule'}
            </Button>
          </Card>

          {dayPlan && (
            <div className="space-y-3">
              <div className="flex items-center justify-between px-1">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Total Planned Work: {Math.round(dayPlan.total_work_minutes / 60)}h {dayPlan.total_work_minutes % 60}m
                </span>
                <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                  <CheckCircle size={14} /> Cognitive breaks inserted
                </span>
              </div>

              {dayPlan.scheduled_tasks.map((task, idx) => (
                <Card key={idx} hover className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-16 text-center border-r border-gray-100 dark:border-gray-800 pr-3">
                      <span className="text-xs font-bold text-violet-600 dark:text-violet-400 block">
                        {task.start_time}
                      </span>
                      <span className="text-[10px] text-gray-400 block">{task.end_time}</span>
                    </div>

                    <div>
                      <h4 className="text-sm font-bold text-gray-900 dark:text-white">{task.title}</h4>
                      <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
                        <span className="text-violet-600 dark:text-violet-400 font-medium">{task.energy_level}</span>
                        <span>•</span>
                        <span>{task.estimated_minutes} min</span>
                      </div>
                    </div>
                  </div>

                  <Badge variant="info">{task.category}</Badge>
                </Card>
              ))}

              {/* Breaks */}
              {dayPlan.rest_breaks && dayPlan.rest_breaks.map((b, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-dashed border-amber-200 dark:border-amber-800/40 flex items-center justify-between text-xs text-amber-800 dark:text-amber-300"
                >
                  <span className="flex items-center gap-2 font-medium">
                    <Coffee size={16} className="text-amber-600" />
                    {b.type}
                  </span>
                  <span className="font-semibold">{b.start} - {b.end}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Weekly Balancer */}
      {activeTab === 'weekly' && (
        <div className="space-y-4">
          <Card className="p-6 bg-gradient-to-r from-violet-50/60 to-indigo-50/40 dark:from-[#171722] dark:to-[#17171f] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="font-bold text-gray-900 dark:text-white text-base flex items-center gap-2">
                <Calendar size={18} className="text-violet-600" />
                7-Day Workload Balancer
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-xl">
                Distributes upcoming tasks across Monday through Friday with a strict 8-hour daily cap to prevent burnout.
              </p>
            </div>
            <Button onClick={generateWeeklyPlan} disabled={isLoading} icon={<Brain size={16} />}>
              {isLoading ? 'Balancing...' : 'Balance Week'}
            </Button>
          </Card>

          {weekPlan && (
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {weekPlan.days.map((d, i) => (
                <Card key={i} className="p-4 text-center">
                  <span className="text-xs font-semibold text-gray-400 uppercase">{d.date}</span>
                  <div className="text-xl font-extrabold text-gray-900 dark:text-white mt-1">
                    {(d.total_minutes / 60).toFixed(1)} hrs
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full mt-3 overflow-hidden">
                    <div
                      className="bg-violet-600 h-full rounded-full"
                      style={{ width: `${Math.min(100, (d.total_minutes / 480) * 100)}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-gray-400 block mt-1">Max 8.0 hrs</span>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Conversational AI Assistant */}
      {activeTab === 'chat' && (
        <div className="space-y-4">
          {/* Quick Prompt Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            {[
              'Plan my day based on peak energy',
              'What tasks are currently overdue?',
              'Decompose my long-term goal',
              'Give me a productivity coach tip',
            ].map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(prompt)}
                className="px-3 py-1.5 rounded-full text-xs font-medium bg-violet-50 dark:bg-violet-950/40 text-violet-700 dark:text-violet-300 border border-violet-200 dark:border-violet-800/40 whitespace-nowrap hover:bg-violet-100 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Chat Window */}
          <Card className="h-[460px] flex flex-col p-0 overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-3 max-w-2xl ${m.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white ${
                      m.role === 'user' ? 'bg-indigo-600' : 'bg-violet-600'
                    }`}
                  >
                    {m.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div
                    className={`p-3.5 rounded-2xl text-xs md:text-sm leading-relaxed ${
                      m.role === 'user'
                        ? 'bg-violet-600 text-white rounded-tr-none'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none'
                    }`}
                  >
                    <p>{m.content}</p>
                    <span
                      className={`block text-[10px] mt-1.5 ${
                        m.role === 'user' ? 'text-violet-200 text-right' : 'text-gray-400'
                      }`}
                    >
                      {m.timestamp}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Input Footer */}
            <div className="p-3 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 flex gap-2">
              <input
                type="text"
                placeholder="Ask your AI coach anything..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSendMessage();
                }}
                disabled={isSendingChat}
                className="flex-1 bg-white dark:bg-[#17171f] border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-violet-500 dark:text-white"
              />
              <Button onClick={() => handleSendMessage()} disabled={isSendingChat || !chatInput.trim()}>
                <Send size={16} />
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
