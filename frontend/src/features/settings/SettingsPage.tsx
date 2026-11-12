import React, { useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { useAuthStore } from '../../store/authStore';
import { useThemeStore } from '../../store/themeStore';
import { apiPut, apiGet } from '../../services/api';
import {
  Settings,
  User,
  Bell,
  Moon,
  Sun,
  Download,
  Shield,
  Check,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user } = useAuthStore();
  const { isDark, setTheme } = useThemeStore();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [timezone, setTimezone] = useState(user?.timezone || 'UTC');
  const [isSaved, setIsSaved] = useState(false);

  // Notifications
  const [notifTask, setNotifTask] = useState(true);
  const [notifHabit, setNotifHabit] = useState(true);
  const [notifFriend, setNotifFriend] = useState(true);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiPut('/auth/me', {
        full_name: fullName,
        bio,
        timezone,
      });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2500);
    } catch {
      // handled
    }
  };

  const handleExportData = async () => {
    try {
      const tasks = await apiGet('/tasks/');
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(tasks, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', 'planwise_backup.json');
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch {
      alert('Export failed');
    }
  };

  return (
    <div className="space-y-6 max-w-3xl animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
          <Settings className="text-violet-600" size={26} />
          Account & App Settings
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Manage your personal workspace, appearance, notifications, and data
        </p>
      </div>

      {/* Profile Card */}
      <Card className="p-6 space-y-4">
        <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <User size={18} className="text-violet-600" />
          Profile Information
        </h3>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Email Address
              </label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none text-gray-400 cursor-not-allowed"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Bio / Focus Area
            </label>
            <textarea
              rows={2}
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="e.g., Software Architect focusing on distributed systems and AI"
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-sm outline-none dark:text-white resize-none"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            {isSaved && (
              <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                <Check size={14} /> Profile updated successfully!
              </span>
            )}
            <Button type="submit" size="sm" className="ml-auto">
              Save Changes
            </Button>
          </div>
        </form>
      </Card>

      {/* Appearance & Theme */}
      <Card className="p-6 space-y-4">
        <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
          {isDark ? <Moon size={18} className="text-violet-600" /> : <Sun size={18} className="text-amber-500" />}
          Appearance & Theme
        </h3>

        <div className="grid grid-cols-2 gap-4">
          <button
            type="button"
            onClick={() => setTheme(false)}
            className={`p-4 rounded-xl border-2 flex items-center gap-3 transition-all ${
              !isDark
                ? 'border-violet-600 bg-violet-50/40 text-violet-900'
                : 'border-gray-200 dark:border-gray-800 text-gray-400 hover:border-gray-300'
            }`}
          >
            <Sun size={20} className="text-amber-500" />
            <div className="text-left">
              <span className="text-sm font-bold block">Light Mode</span>
              <span className="text-[11px] text-gray-400 block">Clean & crisp daytime view</span>
            </div>
          </button>

          <button
            type="button"
            onClick={() => setTheme(true)}
            className={`p-4 rounded-xl border-2 flex items-center gap-3 transition-all ${
              isDark
                ? 'border-violet-600 bg-violet-950/40 text-white'
                : 'border-gray-200 dark:border-gray-800 text-gray-600 hover:border-gray-300'
            }`}
          >
            <Moon size={20} className="text-violet-400" />
            <div className="text-left">
              <span className="text-sm font-bold block">Dark Mode</span>
              <span className="text-[11px] text-gray-400 block">Night & OLED optimized</span>
            </div>
          </button>
        </div>
      </Card>

      {/* Notifications */}
      <Card className="p-6 space-y-4">
        <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Bell size={18} className="text-violet-600" />
          Notification Preferences
        </h3>

        <div className="space-y-3">
          <label className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/40 cursor-pointer">
            <div>
              <span className="text-sm font-semibold text-gray-900 dark:text-white block">
                Task & Deadline Alerts
              </span>
              <span className="text-xs text-gray-400">Receive in-browser reminders before deadlines</span>
            </div>
            <input
              type="checkbox"
              checked={notifTask}
              onChange={(e) => setNotifTask(e.target.checked)}
              className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500"
            />
          </label>

          <label className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/40 cursor-pointer">
            <div>
              <span className="text-sm font-semibold text-gray-900 dark:text-white block">
                Habit Streak Protection
              </span>
              <span className="text-xs text-gray-400">Evening reminder if daily habits are unchecked</span>
            </div>
            <input
              type="checkbox"
              checked={notifHabit}
              onChange={(e) => setNotifHabit(e.target.checked)}
              className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500"
            />
          </label>

          <label className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/40 cursor-pointer">
            <div>
              <span className="text-sm font-semibold text-gray-900 dark:text-white block">
                Friend & Couple Activity
              </span>
              <span className="text-xs text-gray-400">Cheer-ups and partner check-in alerts</span>
            </div>
            <input
              type="checkbox"
              checked={notifFriend}
              onChange={(e) => setNotifFriend(e.target.checked)}
              className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500"
            />
          </label>
        </div>
      </Card>

      {/* Data Export & Privacy */}
      <Card className="p-6 space-y-4">
        <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Shield size={18} className="text-emerald-500" />
          Data Portability & Privacy
        </h3>
        <p className="text-xs text-gray-400">
          Your tasks and personal notes belong to you. Download a complete JSON archive anytime.
        </p>

        <Button variant="secondary" onClick={handleExportData} icon={<Download size={16} />}>
          Export All Tasks & Workspaces (JSON)
        </Button>
      </Card>
    </div>
  );
};
