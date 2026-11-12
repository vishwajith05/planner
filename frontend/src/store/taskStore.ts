import { create } from 'zustand';
import { Task, TaskCreate, TaskUpdate, Category } from '../types';
import { apiGet, apiPost, apiPut, apiDelete } from '../services/api';

interface TaskFilter {
  category?: string;
  priority?: string;
  status?: string;
  search?: string;
  is_completed?: boolean;
}

interface TaskState {
  tasks: Task[];
  categories: Category[];
  filters: TaskFilter;
  isLoading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  fetchCategories: () => Promise<void>;
  createTask: (task: TaskCreate) => Promise<Task>;
  updateTask: (id: string, update: TaskUpdate) => Promise<Task>;
  toggleTask: (id: string) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  duplicateTask: (id: string) => Promise<Task>;
  setFilter: (filters: Partial<TaskFilter>) => void;
  resetFilters: () => void;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  categories: [],
  filters: {},
  isLoading: false,
  error: null,

  fetchTasks: async () => {
    set({ isLoading: true, error: null });
    try {
      const { filters } = get();
      const params: Record<string, unknown> = {};
      if (filters.category) params.category = filters.category;
      if (filters.priority) params.priority = filters.priority;
      if (filters.status) params.status_val = filters.status;
      if (filters.search) params.search = filters.search;
      if (filters.is_completed !== undefined) params.is_completed = filters.is_completed;

      const tasks = await apiGet<Task[]>('/tasks/', params);
      set({ tasks, isLoading: false });
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message || 'Failed to load tasks';
      set({ error: msg, isLoading: false });
    }
  },

  fetchCategories: async () => {
    try {
      const categories = await apiGet<Category[]>('/tasks/categories/');
      set({ categories });
    } catch {
      // fallback default categories if needed
    }
  },

  createTask: async (taskIn: TaskCreate) => {
    const newTask = await apiPost<Task>('/tasks/', taskIn);
    set((state) => ({ tasks: [newTask, ...state.tasks] }));
    return newTask;
  },

  updateTask: async (id: string, update: TaskUpdate) => {
    const updated = await apiPut<Task>(`/tasks/${id}`, update);
    set((state) => ({
      tasks: state.tasks.map((t) => (t.id === id ? updated : t)),
    }));
    return updated;
  },

  toggleTask: async (id: string) => {
    // Optimistic toggle
    set((state) => ({
      tasks: state.tasks.map((t) =>
        t.id === id ? { ...t, is_completed: !t.is_completed } : t
      ),
    }));
    try {
      const res = await apiPut<Task>(`/tasks/${id}/toggle`);
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === id ? res : t)),
      }));
    } catch {
      // Revert on failure
      get().fetchTasks();
    }
  },

  deleteTask: async (id: string) => {
    set((state) => ({ tasks: state.tasks.filter((t) => t.id !== id) }));
    await apiDelete(`/tasks/${id}`);
  },

  duplicateTask: async (id: string) => {
    const duplicated = await apiPost<Task>(`/tasks/${id}/duplicate`);
    set((state) => ({ tasks: [duplicated, ...state.tasks] }));
    return duplicated;
  },

  setFilter: (newFilters) => {
    set((state) => ({ filters: { ...state.filters, ...newFilters } }));
    get().fetchTasks();
  },

  resetFilters: () => {
    set({ filters: {} });
    get().fetchTasks();
  },
}));
