import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { EmptyState } from '../../components/common/EmptyState';
import { apiGet, apiPost, apiPut, apiDelete } from '../../services/api';
import { Goal, Milestone, Priority } from '../../types';
import {
  Target,
  Plus,
  CheckCircle2,
  Calendar,
  Sparkles,
  Trash2,
  Edit2,
  Clock,
  Flag,
  AlertTriangle,
  Layers,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export const GoalsPage: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Create Goal Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createTitle, setCreateTitle] = useState('');
  const [createDesc, setCreateDesc] = useState('');
  const [createCategory, setCreateCategory] = useState('Career');
  const [createPriority, setCreatePriority] = useState<Priority>('medium');
  const [createTargetDate, setCreateTargetDate] = useState('');
  const [createMilestonesInput, setCreateMilestonesInput] = useState('');

  // Edit Goal Modal state
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editCategory, setEditCategory] = useState('Career');
  const [editPriority, setEditPriority] = useState<Priority>('medium');
  const [editTargetDate, setEditTargetDate] = useState('');
  const [editStatus, setEditStatus] = useState<'in_progress' | 'completed' | 'paused'>('in_progress');

  // Add Task to Goal inline state
  const [newTaskTitle, setNewTaskTitle] = useState<{ [goalId: string]: string }>({});
  const [newTaskPriority, setNewTaskPriority] = useState<{ [goalId: string]: Priority }>({});

  // Confirm delete dialog state
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    type: 'goal' | 'task';
    goalId: string;
    milestoneId?: string;
    title: string;
  } | null>(null);

  const fetchGoals = async () => {
    try {
      const data = await apiGet<Goal[]>('/goals');
      // Normalize progress
      const normalized = (data || []).map((g) => ({
        ...g,
        progress_percentage: g.progress_percentage ?? g.progress_percent ?? 0,
        priority: g.priority || 'medium',
        status: g.status || (g.is_completed ? 'completed' : 'in_progress'),
        milestones: g.milestones || [],
      }));
      setGoals(normalized);
    } catch {
      setGoals([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  // ── Goal CRUD ──────────────────────────────────────────────────────────────

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createTitle.trim()) return;

    const msList = createMilestonesInput
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)
      .map((t, idx) => ({
        title: t,
        priority: 'medium',
        is_completed: false,
        order_index: idx + 1,
      }));

    try {
      await apiPost('/goals', {
        title: createTitle.trim(),
        description: createDesc.trim() || undefined,
        category: createCategory,
        priority: createPriority,
        target_date: createTargetDate ? new Date(createTargetDate).toISOString() : undefined,
        status: 'in_progress',
        milestones: msList,
      });
      // Reset form
      setCreateTitle('');
      setCreateDesc('');
      setCreateCategory('Career');
      setCreatePriority('medium');
      setCreateTargetDate('');
      setCreateMilestonesInput('');
      setIsCreateModalOpen(false);
      fetchGoals();
    } catch (err) {
      console.error('Failed to create goal:', err);
    }
  };

  const openEditModal = (goal: Goal) => {
    setEditingGoal(goal);
    setEditTitle(goal.title);
    setEditDesc(goal.description || '');
    setEditCategory(goal.category || 'Career');
    setEditPriority(goal.priority || 'medium');
    setEditTargetDate(goal.target_date ? goal.target_date.split('T')[0] : '');
    setEditStatus(goal.status || 'in_progress');
  };

  const handleUpdateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingGoal || !editTitle.trim()) return;

    try {
      await apiPut(`/goals/${editingGoal.id}`, {
        title: editTitle.trim(),
        description: editDesc.trim() || undefined,
        category: editCategory,
        priority: editPriority,
        target_date: editTargetDate ? new Date(editTargetDate).toISOString() : undefined,
        status: editStatus,
      });
      setEditingGoal(null);
      fetchGoals();
    } catch (err) {
      console.error('Failed to update goal:', err);
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    try {
      await apiDelete(`/goals/${goalId}`);
      setGoals((prev) => prev.filter((g) => g.id !== goalId));
      setDeleteConfirmation(null);
    } catch (err) {
      console.error('Failed to delete goal:', err);
      fetchGoals();
    }
  };

  // ── Milestone / Goal Task Actions ──────────────────────────────────────────

  const handleAddTask = async (goalId: string) => {
    const title = (newTaskTitle[goalId] || '').trim();
    if (!title) return;
    const priority = newTaskPriority[goalId] || 'medium';

    try {
      await apiPost(`/goals/${goalId}/milestones`, {
        title,
        priority,
        is_completed: false,
      });
      setNewTaskTitle((prev) => ({ ...prev, [goalId]: '' }));
      fetchGoals();
    } catch (err) {
      console.error('Failed to add goal task:', err);
    }
  };

  const handleToggleMilestone = async (goalId: string, milestoneId: string) => {
    // Optimistic UI update
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
            progress_percentage: newPct,
            status: newPct === 100 ? 'completed' : 'in_progress',
          };
        }
        return g;
      })
    );

    try {
      await apiPost(`/goals/milestones/${milestoneId}/toggle`);
    } catch {
      fetchGoals();
    }
  };

  const handleDeleteMilestone = async (milestoneId: string) => {
    try {
      await apiDelete(`/goals/milestones/${milestoneId}`);
      setDeleteConfirmation(null);
      fetchGoals();
    } catch (err) {
      console.error('Failed to delete milestone:', err);
      fetchGoals();
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <Target className="text-violet-600" size={26} />
            Goals & Strategic Roadmap
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Define high-level objectives, track milestones, and monitor completion progress
          </p>
        </div>

        <Button onClick={() => setIsCreateModalOpen(true)} icon={<Plus size={16} />}>
          New Goal
        </Button>
      </div>

      {/* Goal Cards */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((n) => (
            <div key={n} className="h-44 rounded-2xl bg-gray-100 dark:bg-gray-800 animate-pulse" />
          ))}
        </div>
      ) : goals.length === 0 ? (
        <EmptyState
          icon={<Target size={32} />}
          title="No goals tracked yet"
          description="Start turning long-term ambitions into reality by setting your first goal."
          actionLabel="Create Goal"
          onAction={() => setIsCreateModalOpen(true)}
        />
      ) : (
        <div className="space-y-5">
          {goals.map((goal) => {
            const pct = Math.round(goal.progress_percentage ?? 0);
            const totalMs = goal.milestones.length;
            const completedMs = goal.milestones.filter((m) => m.is_completed).length;

            return (
              <Card key={goal.id} className="p-5 space-y-4 hover:border-violet-300 dark:hover:border-violet-800/60 transition-all shadow-sm">
                {/* Goal Top Info */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300">
                        {goal.category}
                      </span>
                      {goal.priority && <Badge variant={goal.priority}>{goal.priority}</Badge>}
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                          goal.status === 'completed'
                            ? 'bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300'
                            : goal.status === 'paused'
                            ? 'bg-amber-100 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300'
                            : 'bg-blue-100 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300'
                        }`}
                      >
                        {goal.status}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-gray-900 dark:text-white mt-1">
                      {goal.title}
                    </h3>
                    {goal.description && (
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {goal.description}
                      </p>
                    )}
                  </div>

                  {/* Actions & Target Date */}
                  <div className="flex items-center gap-2 sm:self-start">
                    {goal.target_date && (
                      <div className="flex items-center gap-1 text-xs text-gray-400 mr-2">
                        <Calendar size={13} className="text-violet-500" />
                        <span>{new Date(goal.target_date).toLocaleDateString()}</span>
                      </div>
                    )}
                    <button
                      onClick={() => openEditModal(goal)}
                      title="Edit Goal"
                      className="p-1.5 text-gray-400 hover:text-violet-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() =>
                        setDeleteConfirmation({
                          type: 'goal',
                          goalId: goal.id,
                          title: goal.title,
                        })
                      }
                      title="Delete Goal"
                      className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>

                {/* Progress Bar & Percent */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-gray-500">
                      Overall Progress ({completedMs}/{totalMs} tasks completed)
                    </span>
                    <span className="font-extrabold text-violet-600 dark:text-violet-400">
                      {pct}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-800 h-2.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        pct === 100
                          ? 'bg-emerald-500'
                          : 'bg-gradient-to-r from-violet-600 to-indigo-600'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>

                {/* Goal Tasks / Milestones Checklist */}
                <div className="pt-2 border-t border-gray-100 dark:border-gray-800/80 space-y-2">
                  <div className="space-y-1.5">
                    {goal.milestones.map((ms) => (
                      <div
                        key={ms.id}
                        className="flex items-center justify-between p-2.5 rounded-xl bg-gray-50/70 dark:bg-gray-800/40 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group"
                      >
                        <div
                          onClick={() => handleToggleMilestone(goal.id, ms.id)}
                          className="flex items-center gap-3 flex-1 cursor-pointer overflow-hidden"
                        >
                          <input
                            type="checkbox"
                            checked={ms.is_completed}
                            onChange={() => {}}
                            className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500 cursor-pointer"
                          />
                          <span
                            className={`text-xs font-medium truncate ${
                              ms.is_completed
                                ? 'line-through text-gray-400 dark:text-gray-500'
                                : 'text-gray-800 dark:text-gray-200'
                            }`}
                          >
                            {ms.title}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 ml-2 shrink-0">
                          {ms.priority && <Badge variant={ms.priority}>{ms.priority}</Badge>}
                          <button
                            onClick={() =>
                              setDeleteConfirmation({
                                type: 'task',
                                goalId: goal.id,
                                milestoneId: ms.id,
                                title: ms.title,
                              })
                            }
                            title="Delete Task"
                            className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 p-1 rounded transition-opacity"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Add Task to Goal Inline Bar */}
                  <div className="flex items-center gap-2 pt-1.5">
                    <input
                      type="text"
                      placeholder="Add a milestone or task to this goal..."
                      value={newTaskTitle[goal.id] || ''}
                      onChange={(e) =>
                        setNewTaskTitle({ ...newTaskTitle, [goal.id]: e.target.value })
                      }
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleAddTask(goal.id);
                        }
                      }}
                      className="flex-1 bg-white dark:bg-[#17171f] border border-gray-200 dark:border-gray-700/80 rounded-xl px-3 py-1.5 text-xs outline-none dark:text-white"
                    />
                    <select
                      value={newTaskPriority[goal.id] || 'medium'}
                      onChange={(e) =>
                        setNewTaskPriority({
                          ...newTaskPriority,
                          [goal.id]: e.target.value as Priority,
                        })
                      }
                      className="bg-white dark:bg-[#17171f] border border-gray-200 dark:border-gray-700/80 rounded-xl px-2 py-1.5 text-xs outline-none dark:text-white"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                    <Button
                      size="sm"
                      onClick={() => handleAddTask(goal.id)}
                      disabled={!(newTaskTitle[goal.id] || '').trim()}
                    >
                      Add Task
                    </Button>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* ── Modal: Create Goal ──────────────────────────────────────────────── */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Create New Goal">
        <form onSubmit={handleCreateGoal} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Goal Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Publish SaaS Platform"
              value={createTitle}
              onChange={(e) => setCreateTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              rows={2}
              placeholder="Strategic outcome and motivation..."
              value={createDesc}
              onChange={(e) => setCreateDesc(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white resize-none"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Category
              </label>
              <input
                type="text"
                list="goal-cat-list"
                value={createCategory}
                onChange={(e) => setCreateCategory(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
              />
              <datalist id="goal-cat-list">
                <option value="Career" />
                <option value="Programming" />
                <option value="Education" />
                <option value="Cybersecurity" />
                <option value="Health" />
                <option value="Personal" />
                <option value="Finance" />
              </datalist>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Priority
              </label>
              <select
                value={createPriority}
                onChange={(e) => setCreatePriority(e.target.value as Priority)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Target Date
              </label>
              <input
                type="date"
                value={createTargetDate}
                onChange={(e) => setCreateTargetDate(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Initial Milestones / Tasks (one per line)
            </label>
            <textarea
              rows={3}
              placeholder="Step 1: Finish core backend&#10;Step 2: Deploy to cloud&#10;Step 3: Beta launch"
              value={createMilestonesInput}
              onChange={(e) => setCreateMilestonesInput(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2 text-xs outline-none dark:text-white resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
            <Button type="button" variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Goal</Button>
          </div>
        </form>
      </Modal>

      {/* ── Modal: Edit Goal ────────────────────────────────────────────────── */}
      {editingGoal && (
        <Modal isOpen={!!editingGoal} onClose={() => setEditingGoal(null)} title="Edit Goal Details">
          <form onSubmit={handleUpdateGoal} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Goal Title *
              </label>
              <input
                type="text"
                required
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                rows={2}
                value={editDesc}
                onChange={(e) => setEditDesc(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white resize-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                  Category
                </label>
                <input
                  type="text"
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                  Priority
                </label>
                <select
                  value={editPriority}
                  onChange={(e) => setEditPriority(e.target.value as Priority)}
                  className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                  Target Date
                </label>
                <input
                  type="date"
                  value={editTargetDate}
                  onChange={(e) => setEditTargetDate(e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                  Status
                </label>
                <select
                  value={editStatus}
                  onChange={(e) =>
                    setEditStatus(e.target.value as 'in_progress' | 'completed' | 'paused')
                  }
                  className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
                >
                  <option value="in_progress">In Progress</option>
                  <option value="paused">Paused</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
              <Button type="button" variant="secondary" onClick={() => setEditingGoal(null)}>
                Cancel
              </Button>
              <Button type="submit">Save Changes</Button>
            </div>
          </form>
        </Modal>
      )}

      {/* ── Modal: Delete Confirmation ──────────────────────────────────────── */}
      {deleteConfirmation && (
        <Modal
          isOpen={!!deleteConfirmation}
          onClose={() => setDeleteConfirmation(null)}
          title={`Confirm ${deleteConfirmation.type === 'goal' ? 'Goal' : 'Task'} Deletion`}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-xl text-red-700 dark:text-red-400 text-sm">
              <AlertTriangle size={20} className="shrink-0" />
              <span>
                Are you sure you want to delete <strong>"{deleteConfirmation.title}"</strong>?{' '}
                {deleteConfirmation.type === 'goal'
                  ? 'All associated milestones and tasks will be permanently removed.'
                  : 'Goal progress will be automatically updated.'}
              </span>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="secondary"
                onClick={() => setDeleteConfirmation(null)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => {
                  if (deleteConfirmation.type === 'goal') {
                    handleDeleteGoal(deleteConfirmation.goalId);
                  } else if (deleteConfirmation.milestoneId) {
                    handleDeleteMilestone(deleteConfirmation.milestoneId);
                  }
                }}
              >
                Delete Permanently
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
