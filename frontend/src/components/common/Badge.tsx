import React from 'react';
import { Priority } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | Priority;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const variantStyles = {
    default: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    success: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/40',
    warning: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border border-amber-200 dark:border-amber-800/40',
    danger: 'bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-400 border border-rose-200 dark:border-rose-800/40',
    info: 'bg-violet-50 text-violet-700 dark:bg-violet-950/40 dark:text-violet-400 border border-violet-200 dark:border-violet-800/40',
    // Priorities
    urgent: 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 font-semibold',
    high: 'bg-orange-100 text-orange-700 dark:bg-orange-950/60 dark:text-orange-300',
    medium: 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300',
    low: 'bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300',
  }[variant];

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium tracking-wide ${variantStyles} ${className}`}>
      {children}
    </span>
  );
};
