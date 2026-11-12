import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  CheckSquare,
  Calendar,
  Sparkles,
  Repeat,
  Timer,
  Kanban,
  Grid2X2,
  Target,
  Users2,
  HeartHandshake,
  BarChart3,
  Settings,
  BrainCircuit,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const { user, logout } = useAuthStore();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'Tasks', path: '/tasks', icon: CheckSquare },
    { label: 'Calendar', path: '/calendar', icon: Calendar },
    { label: 'AI Planner', path: '/ai-planner', icon: Sparkles, badge: 'AI' },
    { label: 'Habits', path: '/habits', icon: Repeat },
    { label: 'Focus & Timer', path: '/focus', icon: Timer },
    { label: 'Kanban', path: '/kanban', icon: Kanban },
    { label: 'Eisenhower', path: '/eisenhower', icon: Grid2X2 },
    { label: 'Goals', path: '/goals', icon: Target },
    { label: 'Friend Growth', path: '/friends', icon: Users2, badge: 'New' },
    { label: 'Growth Couple', path: '/couple', icon: HeartHandshake, badge: 'New' },
    { label: 'Analytics', path: '/analytics', icon: BarChart3 },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 h-screen bg-white dark:bg-[#121218] border-r border-gray-100 dark:border-[#27272e] flex flex-col justify-between shrink-0 select-none">
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center px-6 gap-3 border-b border-gray-100 dark:border-gray-800">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-violet-500/20">
            <BrainCircuit size={20} />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-gray-900 dark:text-white flex items-center gap-1.5">
              PlanWise <span className="text-violet-600 dark:text-violet-400 font-extrabold text-xs px-1.5 py-0.5 rounded bg-violet-50 dark:bg-violet-950/50">AI</span>
            </h1>
            <p className="text-[11px] text-gray-400 font-medium leading-none">Smart Productivity</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 font-semibold shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon size={18} className="shrink-0" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-violet-100 dark:bg-violet-900/60 text-violet-700 dark:text-violet-300">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Footer Profile */}
      <div className="p-3 border-t border-gray-100 dark:border-gray-800">
        <div className="flex items-center justify-between p-2 rounded-xl bg-gray-50 dark:bg-gray-800/50">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-violet-600 text-white font-bold text-xs flex items-center justify-center shrink-0">
              {user?.full_name ? user.full_name[0].toUpperCase() : user?.email ? user.email[0].toUpperCase() : 'U'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-gray-900 dark:text-white truncate">
                {user?.full_name || 'Active User'}
              </p>
              <p className="text-[10px] text-gray-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            title="Log Out"
            className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-white dark:hover:bg-gray-700 transition-colors"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};
