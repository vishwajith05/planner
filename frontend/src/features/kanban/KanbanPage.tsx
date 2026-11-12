import React, { useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { useTaskStore } from '../../store/taskStore';
import { Task, TaskStatus } from '../../types';
import {
  Kanban as KanbanIcon,
  Plus,
  Clock,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
} from 'lucide-react';

export const KanbanPage: React.FC = () => {
  const { tasks, fetchTasks, updateTask } = useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, []);

  const columns: Array<{ id: TaskStatus; label: string; color: string }> = [
    { id: 'not_started', label: 'To Do', color: 'border-blue-500' },
    { id: 'in_progress', label: 'In Progress', color: 'border-amber-500' },
    { id: 'completed', label: 'Completed', color: 'border-emerald-500' },
  ];

  const moveTask = async (taskId: string, newStatus: TaskStatus) => {
    await updateTask(taskId, {
      status: newStatus,
      is_completed: newStatus === 'completed',
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
          <KanbanIcon className="text-violet-600" size={26} />
          Kanban Board
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Visualize workflow bottlenecks and progress tasks through execution stages
        </p>
      </div>

      {/* 3 Column Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {columns.map((col) => {
          const colTasks = tasks.filter((t) =>
            col.id === 'completed'
              ? t.is_completed || t.status === 'completed'
              : !t.is_completed && (t.status === col.id || (!t.status && col.id === 'not_started'))
          );

          return (
            <div key={col.id} className="flex flex-col h-[calc(100vh-210px)]">
              {/* Column Header */}
              <div
                className={`p-3 rounded-t-xl bg-white dark:bg-[#17171f] border-t-4 ${col.color} border-x border-b border-gray-100 dark:border-gray-800 flex items-center justify-between shadow-sm`}
              >
                <span className="font-bold text-sm text-gray-900 dark:text-white">{col.label}</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                  {colTasks.length}
                </span>
              </div>

              {/* Column Body / Cards */}
              <div className="flex-1 bg-gray-50/50 dark:bg-[#121218]/40 border-x border-b border-gray-100 dark:border-gray-800 rounded-b-xl p-3 overflow-y-auto space-y-3">
                {colTasks.length === 0 ? (
                  <div className="h-32 flex items-center justify-center text-xs text-gray-400 border border-dashed border-gray-200 dark:border-gray-800 rounded-xl">
                    No tasks in {col.label}
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <Card
                      key={task.id}
                      hover
                      className="p-3.5 space-y-2 bg-white dark:bg-[#17171f] shadow-sm"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300">
                          {task.category}
                        </span>
                        <Badge variant={task.priority}>{task.priority}</Badge>
                      </div>

                      <h4 className="text-sm font-semibold text-gray-900 dark:text-white leading-snug">
                        {task.title}
                      </h4>

                      {task.description && (
                        <p className="text-xs text-gray-400 line-clamp-2">{task.description}</p>
                      )}

                      <div className="pt-2 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between text-xs text-gray-400">
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          {task.estimated_minutes}m
                        </span>

                        {/* Movement Buttons */}
                        <div className="flex items-center gap-1">
                          {col.id !== 'not_started' && (
                            <button
                              onClick={() =>
                                moveTask(
                                  task.id,
                                  col.id === 'completed' ? 'in_progress' : 'not_started'
                                )
                              }
                              title="Move Left"
                              className="p-1 rounded text-gray-400 hover:text-violet-600 hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                              <ArrowLeft size={14} />
                            </button>
                          )}

                          {col.id !== 'completed' && (
                            <button
                              onClick={() =>
                                moveTask(
                                  task.id,
                                  col.id === 'not_started' ? 'in_progress' : 'completed'
                                )
                              }
                              title="Move Right"
                              className="p-1 rounded text-gray-400 hover:text-violet-600 hover:bg-gray-100 dark:hover:bg-gray-800"
                            >
                              <ArrowRight size={14} />
                            </button>
                          )}
                        </div>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
