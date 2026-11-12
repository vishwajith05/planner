import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { AppLayout } from '../components/layout/AppLayout';

// Features
import { Login } from '../features/auth/Login';
import { Register } from '../features/auth/Register';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { TasksPage } from '../features/tasks/TasksPage';
import { CalendarPage } from '../features/calendar/CalendarPage';
import { AIPlannerPage } from '../features/ai-planner/AIPlannerPage';
import { HabitsPage } from '../features/habits/HabitsPage';
import { FocusPage } from '../features/focus/FocusPage';
import { KanbanPage } from '../features/kanban/KanbanPage';
import { EisenhowerPage } from '../features/eisenhower/EisenhowerPage';
import { GoalsPage } from '../features/goals/GoalsPage';
import { FriendGrowthPage } from '../features/friend-growth/FriendGrowthPage';
import { GrowthCouplePage } from '../features/growth-couple/GrowthCouplePage';
import { AnalyticsPage } from '../features/analytics/AnalyticsPage';
import { SettingsPage } from '../features/settings/SettingsPage';

// Protected Route Guard
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-[#0f0f13]">
        <div className="w-8 h-8 border-4 border-violet-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected App Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="tasks" element={<TasksPage />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="ai-planner" element={<AIPlannerPage />} />
        <Route path="habits" element={<HabitsPage />} />
        <Route path="focus" element={<FocusPage />} />
        <Route path="kanban" element={<KanbanPage />} />
        <Route path="eisenhower" element={<EisenhowerPage />} />
        <Route path="goals" element={<GoalsPage />} />
        <Route path="friends" element={<FriendGrowthPage />} />
        <Route path="couple" element={<GrowthCouplePage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
