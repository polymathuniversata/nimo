import React, { createContext, useContext, useEffect, useState } from 'react';
import type { Theme, ThemeContextType } from '../types/theme';
import { secureStorage } from '../lib/secureStorage';

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export { ThemeContext };

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');
  const [actualTheme, setActualTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    // Load theme from storage
    const savedTheme = secureStorage.getTheme() as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;

    let systemTheme: 'light' | 'dark' = 'light';
    if (theme === 'system') {
      systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    const currentTheme = theme === 'system' ? systemTheme : theme;
    setActualTheme(currentTheme);

    // Apply theme class
    root.classList.remove('light', 'dark');
    root.classList.add(currentTheme);

    // Save to storage
    secureStorage.setTheme(theme);
  }, [theme]);

  useEffect(() => {
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = () => {
      if (theme === 'system') {
        const newSystemTheme = mediaQuery.matches ? 'dark' : 'light';
        setActualTheme(newSystemTheme);
        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');
        root.classList.add(newSystemTheme);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, actualTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}