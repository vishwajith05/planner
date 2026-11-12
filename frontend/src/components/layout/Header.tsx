import React, { useState } from 'react';
import {
  Menu,
  Sun,
  Moon,
  Plus,
  Wifi,
  WifiOff,
  Sparkles,
} from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';
import { Button } from '../common/Button';
import { CreateTaskModal } from '../../features/tasks/CreateTaskModal';

interface HeaderProps {
  onToggleMobileMenu: () => void;
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileMenu, title }) => {
  const { isDark, toggleTheme } = useThemeStore();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  React.useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <>
      <header className="h-16 px-4 md:px-8 border-b border-gray-100 dark:border-[#27272e] bg-white/80 dark:bg-[#0f0f13]/80 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between">
        {/* Left: Mobile hamburger + Page Title */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobileMenu}
            className="p-2 -ml-2 rounded-xl text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 md:hidden"
          >
            <Menu size={20} />
          </button>
          <h2 className="text-lg font-bold text-gray-900 dark:text-white capitalize">
            {title || 'Dashboard'}
          </h2>
        </div>

        {/* Right Action Bar */}
        <div className="flex items-center gap-2 md:gap-3">
          {/* Online/Offline Badge */}
          <div
            title={isOnline ? 'Online - Cloud Sync Active' : 'Offline - Local Storage Mode'}
            className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
              isOnline
                ? 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/40'
                : 'bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/40'
            }`}
          >
            {isOnline ? <Wifi size={13} /> : <WifiOff size={13} />}
            <span>{isOnline ? 'Synced' : 'Offline'}</span>
          </div>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            className="p-2 rounded-xl text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {/* Quick Create Task Button */}
          <Button
            size="sm"
            onClick={() => setIsCreateModalOpen(true)}
            icon={<Plus size={16} />}
          >
            <span className="hidden sm:inline">New Task</span>
          </Button>
        </div>
      </header>

      {/* Task Creation Modal */}
      <CreateTaskModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </>
  );
};
