import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { EmptyState } from '../../components/common/EmptyState';
import { apiGet, apiPost, apiPut, apiDelete } from '../../services/api';
import { Habit } from '../../types';
import {
  Flame,
  Plus,
  Repeat,
  CheckCircle2,
  Trophy,
  Calendar,
  Sparkles,
  Trash2,
} from 'lucide-react';

export const HabitsPage: React.FC = () => {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Health');
  const [frequency, setFrequency] = useState<'daily' | 'weekly'>('daily');

  const fetchHabits = async () => {
    try {
      const data = await apiGet<Habit[]>('/habits/');
      setHabits(data);
    } catch {
      // Demo habits
      setHabits([
        {
          id: 'h1',
          user_id: 'u1',
          title: 'Daily LeetCode Problem & Algorithm Practice',
          category: 'Programming',
          frequency: 'daily',
          target_days_per_week: 7,
          streak_count: 14,
          best_streak: 21,
          is_archived: false,
          today_completed: true,
          created_at: new Date().toISOString(),
        },
        {
          id: 'h2',
          user_id: 'u1',
          title: 'Morning 20m Focused Reading & Study',
          category: 'Education',
          frequency: 'daily',
          target_days_per_week: 7,
          streak_count: 8,
          best_streak: 12,
          is_archived: false,
          today_completed: false,
          created_at: new Date().toISOString(),
        },
        {
          id: 'h3',
          user_id: 'u1',
          title: 'Physical Workout & Hydration Target',
          category: 'Health',
          frequency: 'daily',
          target_days_per_week: 5,
          streak_count: 5,
          best_streak: 19,
          is_archived: false,
          today_completed: false,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHabits();
  }, []);

  const handleToggleHabit = async (habitId: string) => {
    // Optimistic toggle
    setHabits((prev) =>
      prev.map((h) => {
        if (h.id === habitId) {
          const nextState = !h.today_completed;
          const newStreak = nextState ? h.streak_count + 1 : Math.max(0, h.streak_count - 1);
          return {
            ...h,
            today_completed: nextState,
            streak_count: newStreak,
            best_streak: Math.max(h.best_streak, newStreak),
          };
        }
        return h;
      })
    );

    try {
      await apiPut(`/habits/${habitId}/toggle`);
    } catch {
      fetchHabits();
    }
  };

  const handleDeleteHabit = async (habitId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setHabits((prev) => prev.filter((h) => h.id !== habitId));
    try {
      await apiDelete(`/habits/${habitId}`);
    } catch {
      fetchHabits();
    }
  };

  const handleCreateHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      await apiPost('/habits/', {
        title: title.trim(),
        category,
        frequency,
        target_days_per_week: frequency === 'daily' ? 7 : 3,
      });
      setTitle('');
      setIsModalOpen(false);
      fetchHabits();
    } catch {
      // handled
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <Repeat className="text-violet-600" size={26} />
            Habit Tracker & Streaks
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Build consistency through uninterrupted daily streak momentum
          </p>
        </div>

        <Button onClick={() => setIsModalOpen(true)} icon={<Plus size={16} />}>
          New Habit
        </Button>
      </div>

      {/* Habit Cards */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-20 rounded-xl bg-gray-100 dark:bg-gray-800 animate-pulse" />
          ))}
        </div>
      ) : habits.length === 0 ? (
        <EmptyState
          icon={<Repeat size={28} />}
          title="No habits tracked yet"
          description="Build positive routines by adding your first daily habit."
          actionLabel="Add Habit"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {habits.map((habit) => (
            <Card
              key={habit.id}
              hover
              className={`p-5 flex items-center justify-between transition-all ${
                habit.today_completed
                  ? 'border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/20 dark:bg-emerald-950/10'
                  : ''
              }`}
            >
              <div className="space-y-1 overflow-hidden pr-3">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300">
                    {habit.category}
                  </span>
                  <span className="text-xs text-gray-400 capitalize">{habit.frequency}</span>
                </div>

                <h4 className="text-sm font-bold text-gray-900 dark:text-white truncate">
                  {habit.title}
                </h4>

                <div className="flex items-center gap-3 text-xs text-gray-400 pt-1">
                  <span className="flex items-center gap-1 font-semibold text-amber-500">
                    <Flame size={14} className="fill-amber-500" />
                    {habit.streak_count} day streak
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1 text-gray-500">
                    <Trophy size={13} />
                    Best: {habit.best_streak}d
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={(e) => handleDeleteHabit(habit.id, e)}
                  title="Delete Habit"
                  className="p-2 text-gray-400 hover:text-red-500 rounded-xl hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                >
                  <Trash2 size={18} />
                </button>

                {/* Toggle Check Button */}
                <button
                  onClick={() => handleToggleHabit(habit.id)}
                  className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all shrink-0 ${
                    habit.today_completed
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30 active:scale-95'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-400 hover:text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-950/40'
                  }`}
                >
                  <CheckCircle2 size={24} />
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Habit">
        <form onSubmit={handleCreateHabit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Habit Name *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Read 15 pages of system design"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Category (Type any custom)
              </label>
              <input
                type="text"
                list="habit-category-options"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g., Health, Meditation, Study"
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-sm outline-none dark:text-white"
              />
              <datalist id="habit-category-options">
                <option value="Health" />
                <option value="Programming" />
                <option value="Education" />
                <option value="Personal" />
                <option value="Work" />
                <option value="Fitness" />
                <option value="Mindfulness" />
              </datalist>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Frequency
              </label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value as 'daily' | 'weekly')}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-sm outline-none dark:text-white"
              >
                <option value="daily">Daily Target</option>
                <option value="weekly">Weekly Target</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Habit</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
