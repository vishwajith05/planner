import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { apiPost } from '../../services/api';
import { ChatMessage } from '../../types';
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
  ArrowRight,
  RotateCcw,
  PlusCircle,
  Target,
  ListTodo,
  TrendingUp,
  Inbox,
} from 'lucide-react';

export const AIPlannerPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'daily' | 'weekly' | 'chat'>('daily');
  const [dayPlan, setDayPlan] = useState<any | null>(null);
  const [weekPlan, setWeekPlan] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Chat Agent state
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        "👋 Hello! I'm your PlanWise AI Productivity Coach.\n\nI can directly manage your tasks, generate an energy-balanced daily schedule, audit overdue workload, or break down long-term goals into milestones.\n\nTry tapping one of the quick actions below to see me in action!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actions: [
        { type: 'suggest_prompt', text: 'Plan my day' },
        { type: 'suggest_prompt', text: 'Show tasks' },
        { type: 'suggest_prompt', text: 'What tasks are overdue?' },
        { type: 'suggest_prompt', text: 'How is my productivity?' },
      ],
    },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isSendingChat, setIsSendingChat] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSendingChat]);

  const generateDailySchedule = async () => {
    setIsLoading(true);
    try {
      const plan = await apiPost<any>('/ai/daily-schedule', {});
      setDayPlan(plan);
    } catch {
      // Empty schedule if API encounters issue or zero tasks
      setDayPlan({
        date: new Date().toISOString().split('T')[0],
        scheduled: [],
        unscheduled: [],
        total_work_minutes: 0,
        break_minutes: 0,
        warnings: ['No pending tasks scheduled.'],
      });
    } finally {
      setIsLoading(false);
    }
  };

  const generateWeeklyPlan = async () => {
    setIsLoading(true);
    try {
      const plan = await apiPost<any>('/ai/weekly-plan', {});
      setWeekPlan(plan);
    } catch {
      setWeekPlan({
        day_plans: [],
        days: [],
        unscheduled: [],
        warnings: ['No pending workload to distribute for this week.'],
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (text?: string) => {
    const msgToSend = (text || chatInput).trim();
    if (!msgToSend) return;

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
      const res = await apiPost<any>('/ai/assistant/chat', { message: msgToSend });
      const botMsg: ChatMessage = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: res.reply || res.response || 'Action processed.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actions: res.actions || [],
        data: res.data,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content:
          "I couldn't reach the agentic scheduler backend right now. Please verify your connection or try again shortly.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSendingChat(false);
    }
  };

  const handleActionClick = (action: any) => {
    if (action.type === 'suggest_prompt' && action.text) {
      handleSendMessage(action.text);
    } else if (action.type === 'navigate' && action.destination) {
      navigate('/' + action.destination);
    } else if (action.type === 'confirm_schedule') {
      navigate('/calendar');
    }
  };

  const scheduledTasks = dayPlan?.scheduled || dayPlan?.scheduled_tasks || [];
  const daysList = weekPlan?.days || weekPlan?.day_plans || [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <Sparkles className="text-violet-600" size={26} />
            AI Productivity Engine & Coach
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Intelligent natural language task creation, cognitive schedule packing, and real-time coaching
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
                Inspects your actual pending database tasks, matches cognitive demand to peak energy windows, and automatically allocates restorative breaks.
              </p>
            </div>
            <Button onClick={generateDailySchedule} disabled={isLoading} icon={<Sparkles size={16} />}>
              {isLoading ? 'Packing Schedule...' : 'Build AI Schedule'}
            </Button>
          </Card>

          {dayPlan && (
            <div className="space-y-3">
              <div className="flex items-center justify-between px-1">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Total Planned Work: {Math.round((dayPlan.total_work_minutes || 0) / 60)}h {(dayPlan.total_work_minutes || 0) % 60}m
                </span>
                <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                  <CheckCircle size={14} /> Energy-aligned slots
                </span>
              </div>

              {scheduledTasks.length > 0 ? (
                scheduledTasks.map((task: any, idx: number) => {
                  const startTime = task.start_time || task.start?.split('T')[1]?.slice(0, 5) || task.start || '09:00';
                  const endTime = task.end_time || task.end?.split('T')[1]?.slice(0, 5) || task.end || '10:00';
                  return (
                    <Card key={idx} hover className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-16 text-center border-r border-gray-100 dark:border-gray-800 pr-3">
                          <span className="text-xs font-bold text-violet-600 dark:text-violet-400 block">
                            {startTime}
                          </span>
                          <span className="text-[10px] text-gray-400 block">{endTime}</span>
                        </div>

                        <div>
                          <h4 className="text-sm font-bold text-gray-900 dark:text-white">{task.title}</h4>
                          <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
                            <span className="text-violet-600 dark:text-violet-400 font-medium">
                              {task.energy_level || 'Deep Focus'}
                            </span>
                            <span>•</span>
                            <span>{task.duration_minutes || task.estimated_minutes || 30} min</span>
                          </div>
                        </div>
                      </div>

                      <Badge variant="info">{task.category || 'Work'}</Badge>
                    </Card>
                  );
                })
              ) : (
                <Card className="p-8 text-center space-y-3">
                  <Inbox size={36} className="mx-auto text-gray-300 dark:text-gray-600" />
                  <h4 className="text-sm font-bold text-gray-800 dark:text-gray-200">
                    No Pending Tasks to Schedule
                  </h4>
                  <p className="text-xs text-gray-400 max-w-md mx-auto">
                    You have no uncompleted tasks currently pending. Add tasks in the Tasks section or switch to the AI Assistant tab to create them naturally.
                  </p>
                  <Button size="sm" onClick={() => navigate('/tasks')} icon={<PlusCircle size={14} />}>
                    Go to Tasks
                  </Button>
                </Card>
              )}

              {/* Breaks */}
              {dayPlan.rest_breaks && dayPlan.rest_breaks.length > 0 && dayPlan.rest_breaks.map((b: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-dashed border-amber-200 dark:border-amber-800/40 flex items-center justify-between text-xs text-amber-800 dark:text-amber-300"
                >
                  <span className="flex items-center gap-2 font-medium">
                    <Coffee size={16} className="text-amber-600" />
                    {b.type || 'Cognitive Rest Interval'}
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
                Distributes upcoming tasks across weekdays with a strict 8-hour daily cap to guarantee manageable sustainable pacing.
              </p>
            </div>
            <Button onClick={generateWeeklyPlan} disabled={isLoading} icon={<Brain size={16} />}>
              {isLoading ? 'Balancing...' : 'Balance Week'}
            </Button>
          </Card>

          {weekPlan && (
            <div>
              {daysList.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  {daysList.map((d: any, i: number) => {
                    const totalMins = d.total_minutes || d.work_minutes || 0;
                    return (
                      <Card key={i} className="p-4 text-center">
                        <span className="text-xs font-semibold text-gray-400 uppercase">
                          {d.date || d.day_name || `Day ${i + 1}`}
                        </span>
                        <div className="text-xl font-extrabold text-gray-900 dark:text-white mt-1">
                          {(totalMins / 60).toFixed(1)} hrs
                        </div>
                        <div className="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full mt-3 overflow-hidden">
                          <div
                            className="bg-violet-600 h-full rounded-full transition-all"
                            style={{ width: `${Math.min(100, (totalMins / 480) * 100)}%` }}
                          />
                        </div>
                        <span className="text-[10px] text-gray-400 block mt-1">Max 8.0 hrs</span>
                      </Card>
                    );
                  })}
                </div>
              ) : (
                <Card className="p-8 text-center space-y-3">
                  <Inbox size={36} className="mx-auto text-gray-300 dark:text-gray-600" />
                  <h4 className="text-sm font-bold text-gray-800 dark:text-gray-200">
                    No Pending Workload Found
                  </h4>
                  <p className="text-xs text-gray-400 max-w-md mx-auto">
                    There are no uncompleted tasks to distribute across this week.
                  </p>
                </Card>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Conversational AI Assistant */}
      {activeTab === 'chat' && (
        <div className="space-y-4">
          {/* Quick Interactive Prompt Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            {[
              { label: '📅 Plan my day', prompt: 'Plan my day' },
              { label: '📋 Show tasks', prompt: 'Show tasks' },
              { label: '⚠️ What tasks are overdue?', prompt: 'What tasks are overdue?' },
              { label: '📊 How is my productivity?', prompt: 'How is my productivity?' },
              { label: '🎯 Break down goal', prompt: 'Break down goal: Master Cloud Architecture' },
              { label: '➕ Create task', prompt: 'Create task: Security Vulnerability Review !high' },
            ].map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(item.prompt)}
                className="px-3 py-1.5 rounded-full text-xs font-semibold bg-violet-50 dark:bg-violet-950/40 text-violet-700 dark:text-violet-300 border border-violet-200 dark:border-violet-800/40 whitespace-nowrap hover:bg-violet-100 transition-colors flex items-center gap-1.5"
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Chat Window */}
          <Card className="h-[520px] flex flex-col p-0 overflow-hidden shadow-sm">
            {/* Chat Messages Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-3 max-w-2xl ${m.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white shadow-sm ${
                      m.role === 'user' ? 'bg-indigo-600' : 'bg-violet-600'
                    }`}
                  >
                    {m.role === 'user' ? <User size={15} /> : <Bot size={15} />}
                  </div>
                  <div
                    className={`p-3.5 rounded-2xl text-xs md:text-sm leading-relaxed space-y-2 ${
                      m.role === 'user'
                        ? 'bg-violet-600 text-white rounded-tr-none'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none border border-gray-200/50 dark:border-gray-700/50'
                    }`}
                  >
                    {/* Message Text with simple Markdown formatting */}
                    <div className="whitespace-pre-wrap space-y-1 font-normal">
                      {m.content.split('\n').map((line, lIdx) => {
                        if (line.startsWith('### ')) {
                          return <h4 key={lIdx} className="font-bold text-sm text-violet-600 dark:text-violet-400 mt-2">{line.replace('### ', '')}</h4>;
                        }
                        return <p key={lIdx}>{line}</p>;
                      })}
                    </div>

                    {/* Interactive Action Pills */}
                    {m.actions && m.actions.length > 0 && (
                      <div className="pt-2 flex flex-wrap gap-1.5">
                        {m.actions.map((act: any, aIdx: number) => {
                          if (act.type === 'suggest_prompt') {
                            return (
                              <button
                                key={aIdx}
                                onClick={() => handleActionClick(act)}
                                className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-violet-100 dark:bg-violet-950/70 text-violet-800 dark:text-violet-200 hover:bg-violet-200 dark:hover:bg-violet-900 transition-colors flex items-center gap-1"
                              >
                                <span>👉</span>
                                <span>{act.text}</span>
                              </button>
                            );
                          }
                          if (act.type === 'navigate') {
                            return (
                              <button
                                key={aIdx}
                                onClick={() => handleActionClick(act)}
                                className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 hover:bg-emerald-200 dark:hover:bg-emerald-900 transition-colors flex items-center gap-1"
                              >
                                <span className="capitalize">View {act.destination}</span>
                                <ArrowRight size={12} />
                              </button>
                            );
                          }
                          if (act.type === 'confirm_schedule') {
                            return (
                              <button
                                key={aIdx}
                                onClick={() => handleActionClick(act)}
                                className="px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 hover:bg-amber-200 transition-colors flex items-center gap-1"
                              >
                                <span>Open Calendar</span>
                                <ArrowRight size={12} />
                              </button>
                            );
                          }
                          return null;
                        })}
                      </div>
                    )}

                    <span
                      className={`block text-[10px] mt-1 ${
                        m.role === 'user' ? 'text-violet-200 text-right' : 'text-gray-400'
                      }`}
                    >
                      {m.timestamp}
                    </span>
                  </div>
                </div>
              ))}

              {/* Pulsing Typing Indicator */}
              {isSendingChat && (
                <div className="flex gap-3 max-w-sm">
                  <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center shrink-0 text-white">
                    <Bot size={15} />
                  </div>
                  <div className="p-3 rounded-2xl bg-gray-100 dark:bg-gray-800 rounded-tl-none flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Footer */}
            <div className="p-3 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 flex items-center gap-2">
              <input
                type="text"
                placeholder="Ask your AI coach: e.g. 'Create task: Deploy SaaS', 'Plan my day'..."
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
