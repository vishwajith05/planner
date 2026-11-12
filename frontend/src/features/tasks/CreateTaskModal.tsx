import React, { useState } from 'react';
import { Modal } from '../../components/common/Modal';
import { Button } from '../../components/common/Button';
import { useTaskStore } from '../../store/taskStore';
import { Priority, Recurrence } from '../../types';
import { Sparkles, Calendar, Clock, Tag } from 'lucide-react';

interface CreateTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({ isOpen, onClose }) => {
  const { createTask, categories } = useTaskStore();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [category, setCategory] = useState('Personal');
  const [estimatedMinutes, setEstimatedMinutes] = useState(30);
  const [dueDate, setDueDate] = useState('');
  const [subtasks, setSubtasks] = useState<Array<{ title: string; is_completed: boolean }>>([]);
  const [newSubtask, setNewSubtask] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      await createTask({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        category,
        estimated_minutes: Number(estimatedMinutes),
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
        recurrence: 'none',
        subtasks,
      });
      // Reset form
      setTitle('');
      setDescription('');
      setPriority('medium');
      setCategory('Personal');
      setDueDate('');
      setSubtasks([]);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddSubtask = () => {
    if (!newSubtask.trim()) return;
    setSubtasks([...subtasks, { title: newSubtask.trim(), is_completed: false }]);
    setNewSubtask('');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Task" maxWidth="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
            Task Title *
          </label>
          <input
            type="text"
            required
            placeholder="e.g., Complete Chapter 4 & Practical Labs"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-violet-500 outline-none dark:text-white"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
            Description & Notes
          </label>
          <textarea
            rows={2}
            placeholder="Key details, links, or context..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2 text-sm focus:ring-2 focus:ring-violet-500 outline-none dark:text-white resize-none"
          />
        </div>

        {/* Priority & Category Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-sm outline-none dark:text-white"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Category (Type any custom category)
            </label>
            <input
              type="text"
              list="task-category-options"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g., Personal, Work, Finance, Design..."
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-sm outline-none dark:text-white"
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
              {categories.map((c) => (
                <option key={c.id} value={c.name} />
              ))}
            </datalist>
          </div>
        </div>

        {/* Due Date & Estimated Minutes */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Due Date
            </label>
            <input
              type="datetime-local"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Duration (minutes)
            </label>
            <input
              type="number"
              min={5}
              step={5}
              value={estimatedMinutes}
              onChange={(e) => setEstimatedMinutes(Number(e.target.value))}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-sm outline-none dark:text-white"
            />
          </div>
        </div>

        {/* Subtasks / Checklist */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
            Subtasks & Checklist
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              placeholder="Add a checklist item..."
              value={newSubtask}
              onChange={(e) => setNewSubtask(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddSubtask();
                }
              }}
              className="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-1.5 text-xs outline-none dark:text-white"
            />
            <Button type="button" size="sm" variant="secondary" onClick={handleAddSubtask}>
              Add
            </Button>
          </div>
          {subtasks.length > 0 && (
            <ul className="space-y-1 max-h-24 overflow-y-auto">
              {subtasks.map((st, i) => (
                <li
                  key={i}
                  className="flex items-center justify-between text-xs py-1 px-2.5 rounded-lg bg-gray-50 dark:bg-gray-800/50"
                >
                  <span className="text-gray-700 dark:text-gray-300 truncate">{st.title}</span>
                  <button
                    type="button"
                    onClick={() => setSubtasks(subtasks.filter((_, idx) => idx !== i))}
                    className="text-gray-400 hover:text-red-500 ml-2"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Create Task'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
