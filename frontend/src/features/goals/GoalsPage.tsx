import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { EmptyState } from '../../components/common/EmptyState';
import { apiGet, apiPost, apiPut } from '../../services/api';
import { Goal } from '../../types';
import {
  Target,
  Plus,
  CheckCircle2,
  Calendar,
  Sparkles,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';

export const GoalsPage: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Career');
  const [milestonesInput, setMilestonesInput] = useState('');

  const fetchGoals = async () => {
    try {
      const data = await apiGet<Goal[]>('/goals/');
      setGoals(data);
    } catch {
      // Demo goals
      setGoals([
        {
          id: 'g1',
          user_id: 'u1',
          title: 'Master Full-Stack Cloud Architecture & AI Engineering',
          category: 'Career',
          progress_percent: 66,
          is_completed: false,
          created_at: new Date().toISOString(),
          milestones: [
            { id: 'm1', goal_id: 'g1', title: 'Complete Python & FastAPI backend mastery', is_completed: true, order_index: 1, created_at: '' },
            { id: 'm2', goal_id: 'g1', title: 'Build production React + TypeScript frontend', is_completed: true, order_index: 2, created_at: '' },
            { id: 'm3', goal_id: 'g1', title: 'Deploy to Cloud & integrate Gemini AI features', is_completed: false, order_index: 3, created_at: '' },
          ],
        },
        {
          id: 'g2',
          user_id: 'u1',
          title: 'Pass Offensive Security Certified Professional (OSCP)',
          category: 'Cybersecurity',
          progress_percent: 40,
          is_completed: false,
          created_at: new Date().toISOString(),
          milestones: [
            { id: 'm4', goal_id: 'g2', title: 'Finish PEN-200 official modules', is_completed: true, order_index: 1, created_at: '' },
            { id: 'm5', goal_id: 'g2', title: 'Complete 30 practice target machines', is_completed: false, order_index: 2, created_at: '' },
          ],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const handleToggleMilestone = async (goalId: string, milestoneId: string) => {
    setGoals((prev) =>
      prev.map((g) => {
        if (g.id === goalId) {
          const updatedMs = g.milestones.map((m) =>
            m.id === milestoneId ? { ...m, is_completed: !m.is_completed } : m
          );
          const completedCount = updatedMs.filter((m) => m.is_completed).length;
          const newPct = updatedMs.length > 0 ? Math.round((completedCount / updatedMs.length) * 100) : 0;
          return {
            ...g,
            milestones: updatedMs,
            progress_percent: newPct,
            is_completed: newPct === 100,
          };
        }
        return g;
      })
    );

    try {
      await apiPut(`/goals/${goalId}/milestones/${milestoneId}/toggle`);
    } catch {
      fetchGoals();
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const msList = milestonesInput
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((t, idx) => ({ title: t, order_index: idx + 1 }));

    try {
      await apiPost('/goals/', {
        title: title.trim(),
        category,
        milestones: msList,
      });
      setTitle('');
      setMilestonesInput('');
      setIsModalOpen(false);
      fetchGoals();
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
            <Target className="text-violet-600" size={26} />
            Goals & Milestones
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Deconstruct high-level aspirations into tangible, measurable steps
          </p>
        </div>

        <Button onClick={() => setIsModalOpen(true)} icon={<Plus size={16} />}>
          New Goal
        </Button>
      </div>

      {/* Goal Cards */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((n) => (
            <div key={n} className="h-36 rounded-2xl bg-gray-100 dark:bg-gray-800 animate-pulse" />
          ))}
        </div>
      ) : goals.length === 0 ? (
        <EmptyState
          icon={<Target size={28} />}
          title="No goals set yet"
          description="Define a big ambition and break it into ordered milestones."
          actionLabel="Create Goal"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="space-y-4">
          {goals.map((goal) => (
            <Card key={goal.id} className="p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300">
                    {goal.category}
                  </span>
                  <h3 className="text-base font-bold text-gray-900 dark:text-white mt-1">
                    {goal.title}
                  </h3>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-sm font-black text-violet-600 dark:text-violet-400">
                    {goal.progress_percent}%
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-100 dark:bg-gray-800 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-violet-600 to-indigo-600 h-full rounded-full transition-all duration-500"
                  style={{ width: `${goal.progress_percent}%` }}
                />
              </div>

              {/* Milestones checklist */}
              <div className="pt-2 border-t border-gray-100 dark:border-gray-800/80 space-y-2">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-2">
                  Key Milestones ({goal.milestones.filter((m) => m.is_completed).length}/{goal.milestones.length})
                </span>

                {goal.milestones.map((ms) => (
                  <div
                    key={ms.id}
                    onClick={() => handleToggleMilestone(goal.id, ms.id)}
                    className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/40 cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={ms.is_completed}
                      onChange={() => {}}
                      className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500 cursor-pointer"
                    />
                    <span
                      className={`text-xs font-medium ${
                        ms.is_completed
                          ? 'line-through text-gray-400'
                          : 'text-gray-800 dark:text-gray-200'
                      }`}
                    >
                      {ms.title}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Goal">
        <form onSubmit={handleCreateGoal} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Goal Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Publish a SaaS product"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-sm outline-none dark:text-white"
            >
              <option value="Career">Career</option>
              <option value="Programming">Programming</option>
              <option value="Education">Education</option>
              <option value="Health">Health</option>
              <option value="Personal">Personal</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Milestones (one per line)
            </label>
            <textarea
              rows={4}
              placeholder="Step 1: Build MVP&#10;Step 2: Collect user feedback&#10;Step 3: Launch on Product Hunt"
              value={milestonesInput}
              onChange={(e) => setMilestonesInput(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2 text-xs outline-none dark:text-white resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Save Goal</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
