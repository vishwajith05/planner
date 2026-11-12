import React, { useEffect, useState } from 'react';
import { useTaskStore } from '../../store/taskStore';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { EmptyState } from '../../components/common/EmptyState';
import { CreateTaskModal } from './CreateTaskModal';
import { Task, Priority } from '../../types';
import {
  Search,
  Plus,
  Filter,
  CheckCircle2,
  Clock,
  Calendar,
  MoreVertical,
  Copy,
  Trash2,
  CheckSquare,
  Sparkles,
} from 'lucide-react';

export const TasksPage: React.FC = () => {
  const {
    tasks,
    categories,
    filters,
    isLoading,
    fetchTasks,
    fetchCategories,
    toggleTask,
    deleteTask,
    duplicateTask,
    setFilter,
    resetFilters,
  } = useTaskStore();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);
  const [quickTitle, setQuickTitle] = useState('');
  const [quickCategory, setQuickCategory] = useState('');
  const [isQuickAdding, setIsQuickAdding] = useState(false);

  useEffect(() => {
    fetchTasks();
    fetchCategories();
  }, []);

  const { createTask } = useTaskStore();

  const handleQuickAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickTitle.trim()) return;
    setIsQuickAdding(true);
    try {
      await createTask({
        title: quickTitle.trim(),
        category: quickCategory.trim() || 'Personal',
        priority: 'medium',
        estimated_minutes: 30,
        recurrence: 'none',
      });
      setQuickTitle('');
      setQuickCategory('');
    } finally {
      setIsQuickAdding(false);
    }
  };

  const categoryList = [
    'All',
    ...Array.from(
      new Set([
        'Personal',
        'Work',
        'Education',
        'Programming',
        ...tasks.map((t) => t.category).filter(Boolean),
        ...categories.map((c) => c.name),
      ])
    ),
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
            Tasks & To-Dos
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Organize, prioritize, and check off your daily workload
          </p>
        </div>

        <Button onClick={() => setIsModalOpen(true)} icon={<Plus size={16} />}>
          Add New Task
        </Button>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by title, description, tags..."
            value={filters.search || ''}
            onChange={(e) => setFilter({ search: e.target.value })}
            className="w-full bg-white dark:bg-[#17171f] border border-gray-200 dark:border-gray-800 rounded-xl pl-10 pr-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-violet-500 dark:text-white shadow-sm"
          />
        </div>

        {/* Priority Filter */}
        <select
          value={filters.priority || ''}
          onChange={(e) => setFilter({ priority: e.target.value || undefined })}
          className="bg-white dark:bg-[#17171f] border border-gray-200 dark:border-gray-800 rounded-xl px-3 py-2.5 text-sm outline-none dark:text-white shadow-sm"
        >
          <option value="">All Priorities</option>
          <option value="urgent">Urgent</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        {/* Completion Filter */}
        <select
          value={
            filters.is_completed === undefined
              ? ''
              : filters.is_completed
              ? 'completed'
              : 'active'
          }
          onChange={(e) => {
            const val = e.target.value;
            setFilter({
              is_completed: val === 'completed' ? true : val === 'active' ? false : undefined,
            });
          }}
          className="bg-white dark:bg-[#17171f] border border-gray-200 dark:border-gray-800 rounded-xl px-3 py-2.5 text-sm outline-none dark:text-white shadow-sm"
        >
          <option value="">All Statuses</option>
          <option value="active">Active Only</option>
          <option value="completed">Completed Only</option>
        </select>
      </div>

      {/* Category Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        {categoryList.map((cat) => {
          const isSelected = (!filters.category && cat === 'All') || filters.category === cat;
          return (
            <button
              key={cat}
              onClick={() => setFilter({ category: cat === 'All' ? undefined : cat })}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                isSelected
                  ? 'bg-violet-600 text-white shadow-sm'
                  : 'bg-white dark:bg-[#17171f] text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 hover:border-violet-300'
              }`}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Quick Type & Add Task */}
      <form
        onSubmit={handleQuickAdd}
        className="flex flex-col sm:flex-row items-center gap-2.5 p-2.5 bg-white dark:bg-[#17171f] border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm"
      >
        <div className="relative flex-1 w-full">
          <input
            type="text"
            placeholder="Type your task here and press Enter..."
            value={quickTitle}
            onChange={(e) => setQuickTitle(e.target.value)}
            className="w-full bg-transparent px-3 py-1.5 text-sm outline-none dark:text-white placeholder-gray-400"
          />
        </div>
        <div className="w-full sm:w-52">
          <input
            type="text"
            list="task-category-options"
            placeholder="Category (type custom)"
            value={quickCategory}
            onChange={(e) => setQuickCategory(e.target.value)}
            className="w-full bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-1.5 text-xs outline-none dark:text-white"
          />
          <datalist id="task-category-options">
            <option value="Personal" />
            <option value="Work" />
            <option value="Education" />
            <option value="Programming" />
            <option value="Cybersecurity" />
            <option value="Research" />
            <option value="Health" />
            <option value="Finance" />
            <option value="Fitness" />
            <option value="Design" />
          </datalist>
        </div>
        <Button
          type="submit"
          size="sm"
          disabled={!quickTitle.trim() || isQuickAdding}
          icon={<Plus size={15} />}
        >
          {isQuickAdding ? 'Adding...' : 'Add'}
        </Button>
      </form>

      {/* Task List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-16 rounded-xl bg-gray-100 dark:bg-gray-800/50 animate-pulse" />
          ))}
        </div>
      ) : tasks.length === 0 ? (
        <EmptyState
          icon={<CheckSquare size={28} />}
          title="No tasks found"
          description="Create your first task or try clearing your search and filters."
          actionLabel="Add New Task"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="space-y-2.5">
          {tasks.map((task) => (
            <div
              key={task.id}
              className={`relative flex items-center justify-between p-4 rounded-xl bg-white dark:bg-[#17171f] border transition-all shadow-sm ${
                task.is_completed
                  ? 'border-gray-100 dark:border-gray-800/60 opacity-60'
                  : 'border-gray-200 dark:border-gray-800 hover:border-violet-200 dark:hover:border-violet-900/40'
              }`}
            >
              {/* Left: Checkbox + Title + Metadata */}
              <div className="flex items-center gap-3.5 overflow-hidden flex-1">
                <input
                  type="checkbox"
                  checked={task.is_completed}
                  onChange={() => toggleTask(task.id)}
                  className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500 cursor-pointer"
                />

                <div className="overflow-hidden flex-1">
                  <div className="flex items-center gap-2">
                    <p
                      className={`text-sm font-semibold truncate ${
                        task.is_completed
                          ? 'line-through text-gray-400 dark:text-gray-500'
                          : 'text-gray-900 dark:text-white'
                      }`}
                    >
                      {task.title}
                    </p>
                    <Badge variant={task.priority}>{task.priority}</Badge>
                  </div>

                  {task.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                      {task.description}
                    </p>
                  )}

                  <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                    <span className="font-medium text-gray-600 dark:text-gray-300">
                      {task.category}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock size={12} />
                      {task.estimated_minutes}m
                    </span>
                    {task.due_date && (
                      <>
                        <span>•</span>
                        <span className="flex items-center gap-1 text-violet-600 dark:text-violet-400">
                          <Calendar size={12} />
                          {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      </>
                    )}
                    {task.subtasks && task.subtasks.length > 0 && (
                      <>
                        <span>•</span>
                        <span>
                          {task.subtasks.filter((s) => s.is_completed).length}/{task.subtasks.length} subtasks
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Right: Actions */}
              <div className="flex items-center gap-1 ml-3">
                <button
                  onClick={() => duplicateTask(task.id)}
                  title="Duplicate Task"
                  className="p-1.5 text-gray-400 hover:text-violet-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <Copy size={16} />
                </button>
                <button
                  onClick={() => deleteTask(task.id)}
                  title="Delete Task"
                  className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <CreateTaskModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
};
