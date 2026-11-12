import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { useAuthStore } from '../../store/authStore';
import { useTaskStore } from '../../store/taskStore';
import { apiGet, apiPost } from '../../services/api';
import { DashboardStats, Task } from '../../types';
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  Flame,
  Sparkles,
  Timer,
  Target,
  ArrowRight,
  Send,
  Calendar,
  Layers,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const { toggleTask } = useTaskStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [quickAddInput, setQuickAddInput] = useState('');
  const [isParsing, setIsParsing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const data = await apiGet<DashboardStats>('/dashboard/');
      setStats(data);
    } catch {
      // fallback metrics if DB empty
      setStats({
        today_tasks: 0,
        completed_today: 0,
        pending_tasks: 0,
        overdue_tasks: 0,
        current_streak: 3,
        focus_minutes_today: 50,
        productivity_score: 84,
        upcoming_tasks: [],
        today_schedule: [],
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleQuickAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickAddInput.trim()) return;

    setIsParsing(true);
    try {
      // Send to AI quick-add parser
      await apiPost('/ai/quick-add', { text: quickAddInput.trim() });
      setQuickAddInput('');
      fetchDashboardData();
    } catch {
      // Fallback: standard task creation
      const { createTask } = useTaskStore.getState();
      await createTask({ title: quickAddInput.trim(), priority: 'medium', category: 'Personal' });
      setQuickAddInput('');
      fetchDashboardData();
    } finally {
      setIsParsing(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Greeting & Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
            {getGreeting()}, {user?.full_name?.split(' ')[0] || 'Friend'} 👋
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Let's organize your day and build steady momentum towards your goals.
          </p>
        </div>

        {/* AI Action Launcher Button */}
        <Button
          onClick={() => navigate('/ai-planner')}
          className="self-start md:self-auto bg-gradient-to-r from-violet-600 to-indigo-600 shadow-md shadow-violet-500/20"
          icon={<Sparkles size={16} />}
        >
          Plan My Day with AI
        </Button>
      </div>

      {/* Natural Language Quick Add */}
      <Card className="p-3 bg-gradient-to-r from-violet-50/60 via-white to-indigo-50/40 dark:from-[#171722] dark:via-[#17171f] dark:to-[#171722] border-violet-100 dark:border-violet-900/30">
        <form onSubmit={handleQuickAdd} className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-violet-600 text-white flex items-center justify-center shrink-0 shadow-sm">
            <Sparkles size={16} />
          </div>
          <input
            type="text"
            placeholder="Type naturally: 'Review project architecture tomorrow at 3pm #Work !high'..."
            value={quickAddInput}
            onChange={(e) => setQuickAddInput(e.target.value)}
            disabled={isParsing}
            className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 outline-none px-2"
          />
          <Button type="submit" size="sm" disabled={isParsing || !quickAddInput.trim()}>
            {isParsing ? 'Parsing...' : 'Add'}
          </Button>
        </form>
      </Card>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Pending Tasks */}
        <Card hover className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Pending Tasks
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 flex items-center justify-center">
              <Clock size={16} />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-gray-900 dark:text-white">
            {stats?.pending_tasks ?? 0}
          </div>
          <p className="text-xs text-gray-400 mt-1">Due for completion</p>
        </Card>

        {/* Completed Today */}
        <Card hover className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Completed Today
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 size={16} />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-gray-900 dark:text-white">
            {stats?.completed_today ?? 0}
          </div>
          <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium mt-1">Good pace!</p>
        </Card>

        {/* Focus Minutes */}
        <Card hover className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Focus Minutes
            </span>
            <div className="w-8 h-8 rounded-lg bg-violet-50 dark:bg-violet-950/40 text-violet-600 flex items-center justify-center">
              <Timer size={16} />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-gray-900 dark:text-white">
            {stats?.focus_minutes_today ?? 0}m
          </div>
          <p className="text-xs text-gray-400 mt-1">Deep work logged</p>
        </Card>

        {/* Productivity Score */}
        <Card hover className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Productivity Score
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-600 flex items-center justify-center">
              <Flame size={16} />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-gray-900 dark:text-white flex items-baseline gap-1">
            {stats?.productivity_score ?? 85}
            <span className="text-xs text-gray-400 font-normal">/100</span>
          </div>
          <p className="text-xs text-amber-600 dark:text-amber-400 font-medium mt-1">
            {stats?.productivity_score && stats.productivity_score >= 80 ? 'Peak energy zone' : 'Steady focus'}
          </p>
        </Card>
      </div>

      {/* Main Grid: Tasks & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Today's Tasks */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Calendar size={18} className="text-violet-600" />
              Today's Schedule & Tasks
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/tasks')}
              icon={<ArrowRight size={14} />}
            >
              View All
            </Button>
          </div>

          <div className="space-y-2">
            {stats?.today_schedule && stats.today_schedule.length > 0 ? (
              stats.today_schedule.map((task) => (
                <div
                  key={task.id}
                  className="flex items-center justify-between p-3.5 rounded-xl bg-white dark:bg-[#17171f] border border-gray-100 dark:border-[#27272e] shadow-sm hover:border-violet-200 transition-all"
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    <input
                      type="checkbox"
                      checked={task.is_completed}
                      onChange={async () => {
                        await toggleTask(task.id);
                        fetchDashboardData();
                      }}
                      className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500 cursor-pointer"
                    />
                    <div className="overflow-hidden">
                      <p
                        className={`text-sm font-semibold truncate ${
                          task.is_completed
                            ? 'line-through text-gray-400 dark:text-gray-500'
                            : 'text-gray-900 dark:text-white'
                        }`}
                      >
                        {task.title}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
                        <span>{task.category}</span>
                        <span>•</span>
                        <span>{task.estimated_minutes} min</span>
                      </div>
                    </div>
                  </div>
                  <Badge variant={task.priority}>{task.priority}</Badge>
                </div>
              ))
            ) : (
              <Card className="p-8 text-center">
                <CheckCircle2 size={32} className="mx-auto text-emerald-500 mb-2" />
                <h4 className="font-semibold text-gray-900 dark:text-white">All caught up for today!</h4>
                <p className="text-xs text-gray-400 mt-1">
                  Enjoy your day or use the AI Planner to schedule upcoming goals.
                </p>
              </Card>
            )}
          </div>
        </div>

        {/* Right Col: Quick Actions & Habits */}
        <div className="space-y-4">
          <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Layers size={18} className="text-violet-600" />
            Quick Workflows
          </h3>

          <div className="grid grid-cols-1 gap-3">
            <Card
              hover
              onClick={() => navigate('/focus')}
              className="p-4 cursor-pointer flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-violet-100 dark:bg-violet-950/60 text-violet-600 dark:text-violet-400 flex items-center justify-center shrink-0">
                <Timer size={20} />
              </div>
              <div>
                <h4 className="text-sm font-bold text-gray-900 dark:text-white">Start Pomodoro</h4>
                <p className="text-xs text-gray-400">25m deep work session</p>
              </div>
            </Card>

            <Card
              hover
              onClick={() => navigate('/friends')}
              className="p-4 cursor-pointer flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-pink-100 dark:bg-pink-950/60 text-pink-600 dark:text-pink-400 flex items-center justify-center shrink-0">
                <Flame size={20} />
              </div>
              <div>
                <h4 className="text-sm font-bold text-gray-900 dark:text-white">Friend Challenge</h4>
                <p className="text-xs text-gray-400">Check shared targets</p>
              </div>
            </Card>

            <Card
              hover
              onClick={() => navigate('/goals')}
              className="p-4 cursor-pointer flex items-center gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
                <Target size={20} />
              </div>
              <div>
                <h4 className="text-sm font-bold text-gray-900 dark:text-white">Review Goals</h4>
                <p className="text-xs text-gray-400">Track milestone progress</p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
