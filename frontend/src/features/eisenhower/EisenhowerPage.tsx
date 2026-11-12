import React, { useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { useTaskStore } from '../../store/taskStore';
import { Grid2X2, CheckCircle2, Clock } from 'lucide-react';

export const EisenhowerPage: React.FC = () => {
  const { tasks, fetchTasks, toggleTask } = useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, []);

  const activeTasks = tasks.filter((t) => !t.is_completed);

  // Quadrant 1: Urgent & Important (Urgent priority)
  const q1 = activeTasks.filter((t) => t.priority === 'urgent');

  // Quadrant 2: Important, Not Urgent (High priority)
  const q2 = activeTasks.filter((t) => t.priority === 'high');

  // Quadrant 3: Urgent, Not Important (Medium priority)
  const q3 = activeTasks.filter((t) => t.priority === 'medium');

  // Quadrant 4: Neither (Low priority)
  const q4 = activeTasks.filter((t) => t.priority === 'low');

  const quadrants = [
    {
      title: 'Quadrant 1: Do First',
      subtitle: 'Urgent & Important (Crises, Deadlines)',
      color: 'border-red-500 bg-red-50/20 dark:bg-red-950/10',
      badge: 'urgent' as const,
      tasks: q1,
    },
    {
      title: 'Quadrant 2: Schedule',
      subtitle: 'Important, Not Urgent (Growth, Strategy)',
      color: 'border-violet-500 bg-violet-50/20 dark:bg-violet-950/10',
      badge: 'high' as const,
      tasks: q2,
    },
    {
      title: 'Quadrant 3: Delegate',
      subtitle: 'Urgent, Not Important (Interruptions)',
      color: 'border-amber-500 bg-amber-50/20 dark:bg-amber-950/10',
      badge: 'medium' as const,
      tasks: q3,
    },
    {
      title: 'Quadrant 4: Don\'t Do / Eliminate',
      subtitle: 'Not Urgent & Not Important (Time Wasters)',
      color: 'border-blue-500 bg-blue-50/20 dark:bg-blue-950/10',
      badge: 'low' as const,
      tasks: q4,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
          <Grid2X2 className="text-violet-600" size={26} />
          Eisenhower Matrix
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Triage your tasks by urgency and importance to focus on high-leverage activities
        </p>
      </div>

      {/* 2x2 Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {quadrants.map((quad, idx) => (
          <div
            key={idx}
            className={`border-2 rounded-2xl p-4 flex flex-col h-[340px] shadow-sm ${quad.color}`}
          >
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-800">
              <div>
                <h3 className="font-bold text-sm text-gray-900 dark:text-white">{quad.title}</h3>
                <p className="text-[11px] text-gray-500 dark:text-gray-400">{quad.subtitle}</p>
              </div>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-white dark:bg-[#17171f] text-gray-700 dark:text-gray-300 shadow-xs border border-gray-100 dark:border-gray-800">
                {quad.tasks.length}
              </span>
            </div>

            <div className="flex-1 overflow-y-auto pt-3 space-y-2">
              {quad.tasks.length === 0 ? (
                <div className="h-full flex items-center justify-center text-xs text-gray-400">
                  No tasks in this quadrant
                </div>
              ) : (
                quad.tasks.map((task) => (
                  <div
                    key={task.id}
                    className="p-3 rounded-xl bg-white dark:bg-[#17171f] border border-gray-100 dark:border-gray-800 flex items-center justify-between shadow-xs hover:border-violet-200"
                  >
                    <div className="flex items-center gap-2.5 overflow-hidden pr-2">
                      <input
                        type="checkbox"
                        checked={task.is_completed}
                        onChange={() => toggleTask(task.id)}
                        className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500 cursor-pointer"
                      />
                      <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 truncate">
                        {task.title}
                      </span>
                    </div>
                    <span className="text-[10px] text-gray-400 shrink-0">{task.category}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
