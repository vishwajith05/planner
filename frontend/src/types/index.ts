// ── Core Entities ───────────────────────────────────────────────────────────

export type Priority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskStatus = 'not_started' | 'in_progress' | 'completed' | 'cancelled';
export type Recurrence = 'none' | 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface Subtask {
  id: string;
  title: string;
  is_completed: boolean;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  notes?: string;
  priority: Priority;
  status: TaskStatus;
  category: string;
  tags?: string;
  list_name: string;
  estimated_minutes: number;
  actual_minutes: number;
  start_time?: string;
  due_date?: string;
  reminder_time?: string;
  recurrence: Recurrence;
  subtasks: Subtask[];
  is_completed: boolean;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  notes?: string;
  priority?: Priority;
  status?: TaskStatus;
  category?: string;
  tags?: string;
  list_name?: string;
  estimated_minutes?: number;
  due_date?: string;
  reminder_time?: string;
  recurrence?: Recurrence;
  subtasks?: Omit<Subtask, 'id'>[];
}

export interface TaskUpdate extends Partial<TaskCreate> {
  is_completed?: boolean;
  actual_minutes?: number;
  status?: TaskStatus;
}

export interface Category {
  id: string;
  name: string;
  color: string;
  icon: string;
  is_default: boolean;
  user_id?: string;
}

// ── User ─────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name?: string;
  bio?: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  user: User;
}

// ── Habit ─────────────────────────────────────────────────────────────────────

export interface Habit {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  category: string;
  frequency: 'daily' | 'weekly';
  target_days_per_week: number;
  streak_count: number;
  best_streak: number;
  is_archived: boolean;
  today_completed?: boolean;
  completions_this_week?: number;
  created_at: string;
}

// ── Focus ─────────────────────────────────────────────────────────────────────

export type PomodoroMode = 'focus' | 'short_break' | 'long_break';

export interface FocusSession {
  id: string;
  user_id: string;
  task_id?: string;
  task_title?: string;
  duration_minutes: number;
  mode: string;
  completed: boolean;
  started_at: string;
  ended_at?: string;
}

// ── Goal ─────────────────────────────────────────────────────────────────────

export interface Milestone {
  id: string;
  goal_id: string;
  title: string;
  is_completed: boolean;
  order_index: number;
  created_at: string;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  category: string;
  target_date?: string;
  progress_percent: number;
  is_completed: boolean;
  milestones: Milestone[];
  created_at: string;
}

// ── Calendar ─────────────────────────────────────────────────────────────────

export interface CalendarEvent {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  is_fixed: boolean;
  color?: string;
  event_type?: string;
  created_at: string;
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export interface AnalyticsData {
  period: string;
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  total_focus_minutes: number;
  habit_streak_average: number;
  productivity_score: number;
  category_breakdown: Record<string, { total: number; completed: number; rate: number }>;
  daily_completions: Array<{ date: string; count: number }>;
  peak_hour?: number;
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export interface DashboardStats {
  today_tasks: number;
  completed_today: number;
  pending_tasks: number;
  overdue_tasks: number;
  current_streak: number;
  focus_minutes_today: number;
  productivity_score: number;
  upcoming_tasks: Task[];
  today_schedule: Task[];
}

// ── AI ─────────────────────────────────────────────────────────────────────────

export interface AIScheduledTask {
  task_id: string;
  title: string;
  start_time: string;
  end_time: string;
  energy_level: string;
  category: string;
  estimated_minutes: number;
}

export interface AIDayPlan {
  date: string;
  scheduled_tasks: AIScheduledTask[];
  skipped_tasks: string[];
  total_work_minutes: number;
  rest_breaks: Array<{ start: string; end: string; type: string }>;
  warnings: string[];
}

export interface AIWeekPlan {
  days: Array<{ date: string; tasks: AIScheduledTask[]; total_minutes: number }>;
  overflow_tasks: string[];
  warnings: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  actions?: Array<{ label: string; action: string; params?: Record<string, unknown> }>;
}

// ── Friend Growth ─────────────────────────────────────────────────────────────

export interface FriendProfile {
  id: string;
  email: string;
  full_name?: string;
  bio?: string;
  friendship_id?: string;
  friendship_status?: string;
}

export interface FriendRequest {
  friendship_id: string;
  requester_id: string;
  requester_email: string;
  requester_name?: string;
  sent_at: string;
}

export interface SharedChallenge {
  id: string;
  creator_id: string;
  title: string;
  description?: string;
  category: string;
  duration_days: string;
  daily_target?: string;
  weekly_target?: string;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  my_progress: string;
  participants: Array<{
    user_id: string;
    name: string;
    progress_percent: string;
    days_completed: string;
  }>;
  created_at: string;
}

export interface EncouragementMessage {
  id: string;
  sender_id: string;
  sender_name: string;
  recipient_id: string;
  challenge_id?: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

// ── Growth Couple ─────────────────────────────────────────────────────────────

export interface CoupleRelationship {
  id: string;
  invite_code: string;
  status: string;
  partner_a_id: string;
  partner_b_id: string;
  partner_a: { id: string; name: string; email: string } | null;
  partner_b: { id: string; name: string; email: string } | null;
  is_partner_a: boolean;
  created_at: string;
  activated_at?: string;
}

export interface SharedGoal {
  id: string;
  couple_id: string;
  creator_id: string;
  title: string;
  description?: string;
  category: string;
  target_date?: string;
  partner_a_progress: number;
  partner_b_progress: number;
  my_progress: number;
  combined_progress: number;
  is_completed: boolean;
  created_at: string;
}

export interface SharedHabit {
  id: string;
  couple_id: string;
  title: string;
  description?: string;
  frequency: string;
  partner_a_streak: number;
  partner_b_streak: number;
  my_streak: number;
  today_partner_a_done: boolean;
  today_partner_b_done: boolean;
  today_i_done: boolean;
  is_active: boolean;
  created_at: string;
}

export interface CoupleCheckIn {
  id: string;
  user_id: string;
  user_name: string;
  is_me: boolean;
  mood: string;
  gratitude?: string;
  win_of_day?: string;
  support_needed?: string;
  check_in_date: string;
  created_at: string;
}

export interface CoupleChallenge {
  id: string;
  couple_id: string;
  title: string;
  description?: string;
  duration_days: number;
  partner_a_progress: number;
  partner_b_progress: number;
  my_progress: number;
  combined_progress: number;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  created_at: string;
}
