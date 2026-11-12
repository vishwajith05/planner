import { create } from 'zustand';

interface ThemeState {
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (dark: boolean) => void;
}

export const useThemeStore = create<ThemeState>((set) => {
  const initialDark = localStorage.getItem('planwise_theme') === 'dark' ||
    (!localStorage.getItem('planwise_theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);

  if (initialDark) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  return {
    isDark: initialDark,
    toggleTheme: () => set((state) => {
      const next = !state.isDark;
      if (next) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('planwise_theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('planwise_theme', 'light');
      }
      return { isDark: next };
    }),
    setTheme: (dark: boolean) => {
      if (dark) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('planwise_theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('planwise_theme', 'light');
      }
      set({ isDark: dark });
    },
  };
});
