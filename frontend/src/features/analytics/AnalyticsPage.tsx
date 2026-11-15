import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { apiGet } from '../../services/api';
import { AnalyticsData } from '../../types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
} from 'recharts';
import { BarChart3, TrendingUp, Clock, Flame, CheckCircle2, Inbox } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState<'today' | 'week' | 'month'>('week');
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true);
      try {
        const res = await apiGet<AnalyticsData>(`/analytics/?period=${period}`);
        setData(res);
      } catch {
        // Zero-state baseline when user has no activity yet or offline
        setData({
          period,
          total_tasks: 0,
          completed_tasks: 0,
          completion_rate: 0,
          total_focus_minutes: 0,
          habit_streak_average: 0,
          productivity_score: 0,
          peak_hour: undefined,
          category_breakdown: {},
          daily_completions: [],
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, [period]);

  const categoryChartData = data?.category_breakdown
    ? Array.isArray(data.category_breakdown)
      ? data.category_breakdown.map((item: any) => ({
          name: item.category || item.name || 'General',
          completed: item.completed_tasks ?? item.completed ?? 0,
          total: item.total_tasks ?? item.total ?? 0,
        }))
      : Object.entries(data.category_breakdown).map(([name, val]: [string, any]) => ({
          name,
          completed: val?.completed ?? val?.completed_tasks ?? 0,
          total: val?.total ?? val?.total_tasks ?? 0,
        }))
    : [];

  const hasCompletions = data?.daily_completions && data.daily_completions.some((d) => d.count > 0);
  const hasCategories = categoryChartData.length > 0 && categoryChartData.some((c) => c.total > 0);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="text-violet-600" size={26} />
            Productivity Analytics
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Real metrics computed from your tasks, habits, and focus sessions
          </p>
        </div>

        {/* Period Switcher */}
        <div className="bg-gray-100 dark:bg-gray-800 p-1 rounded-xl flex items-center gap-1 text-xs font-semibold">
          {(['today', 'week', 'month'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3.5 py-1.5 rounded-lg capitalize transition-all ${
                period === p
                  ? 'bg-white dark:bg-[#17171f] text-violet-600 dark:text-violet-400 shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {p === 'week' ? 'This Week' : p === 'month' ? 'This Month' : 'Today'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <span className="text-xs font-semibold text-gray-400 uppercase">Completion Rate</span>
          <div className="text-2xl font-black text-gray-900 dark:text-white mt-1">
            {data ? `${Math.round(data.completion_rate)}%` : '0%'}
          </div>
          <p className="text-xs text-gray-400 font-semibold mt-0.5">
            {data && data.total_tasks > 0
              ? `${data.completed_tasks} of ${data.total_tasks} completed`
              : '0 tasks recorded'}
          </p>
        </Card>

        <Card className="p-4">
          <span className="text-xs font-semibold text-gray-400 uppercase">Total Focus Logged</span>
          <div className="text-2xl font-black text-gray-900 dark:text-white mt-1">
            {data ? `${(data.total_focus_minutes / 60).toFixed(1)} hrs` : '0.0 hrs'}
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            {data && data.total_focus_minutes > 0
              ? `${data.total_focus_minutes} focus minutes`
              : '0 focus sessions'}
          </p>
        </Card>

        <Card className="p-4">
          <span className="text-xs font-semibold text-gray-400 uppercase">Avg Habit Streak</span>
          <div className="text-2xl font-black text-gray-900 dark:text-white mt-1">
            {data ? `${Math.round(data.habit_streak_average)} days` : '0 days'}
          </div>
          <p className="text-xs text-gray-400 font-semibold mt-0.5">
            {data && data.habit_streak_average > 0 ? 'Active momentum' : 'No habit streaks yet'}
          </p>
        </Card>

        <Card className="p-4">
          <span className="text-xs font-semibold text-gray-400 uppercase">Peak Focus Window</span>
          <div className="text-2xl font-black text-violet-600 dark:text-violet-400 mt-1">
            {data?.peak_hour != null ? `${data.peak_hour}:00` : 'None logged'}
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            {data?.peak_hour != null ? 'Optimal deep work window' : 'Log focus sessions to compute'}
          </p>
        </Card>
      </div>

      {/* Velocity Chart & Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Completion Velocity */}
        <Card className="p-5 space-y-4">
          <h3 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-2">
            <TrendingUp size={16} className="text-violet-600" />
            Task Completion Velocity
          </h3>
          <div className="h-64 w-full flex items-center justify-center">
            {hasCompletions ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data?.daily_completions || []}>
                  <defs>
                    <linearGradient id="velocityGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.15} />
                  <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#17171f',
                      borderRadius: '12px',
                      border: 'none',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#8B5CF6"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#velocityGrad)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center p-6 space-y-2">
                <Inbox size={32} className="mx-auto text-gray-300 dark:text-gray-600" />
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                  No completed tasks in this period yet
                </p>
                <p className="text-[11px] text-gray-400 max-w-xs">
                  Complete your scheduled tasks to visualize your daily execution momentum.
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Category Breakdown */}
        <Card className="p-5 space-y-4">
          <h3 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-500" />
            Category Execution Breakdown
          </h3>
          <div className="h-64 w-full flex items-center justify-center">
            {hasCategories ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.15} />
                  <XAxis dataKey="name" stroke="#888888" fontSize={11} tickLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#17171f',
                      borderRadius: '12px',
                      border: 'none',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="completed" fill="#8B5CF6" radius={[6, 6, 0, 0]} name="Completed Tasks" />
                  <Bar dataKey="total" fill="#E5E7EB" radius={[6, 6, 0, 0]} name="Total Tasks" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center p-6 space-y-2">
                <BarChart3 size={32} className="mx-auto text-gray-300 dark:text-gray-600" />
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                  No categorized tasks recorded yet
                </p>
                <p className="text-[11px] text-gray-400 max-w-xs">
                  Create tasks with categories (e.g. Work, Study, Health) to see your distribution breakdown.
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
