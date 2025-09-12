// React import not required with new JSX transform
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useTheme } from '@/hooks/useTheme';
import { Sun, Moon, Monitor, Palette } from 'lucide-react';

export function ThemeToggle() {
  const { theme, setTheme, actualTheme } = useTheme();

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun className="h-4 w-4" />;
      case 'dark':
        return <Moon className="h-4 w-4" />;
      case 'system':
        return <Monitor className="h-4 w-4" />;
      default:
        return <Palette className="h-4 w-4" />;
    }
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light':
        return 'Light';
      case 'dark':
        return 'Dark';
      case 'system':
        return `System (${actualTheme})`;
      default:
        return 'Theme';
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="h-9 px-2 rounded-md border border-border bg-card/10 hover:bg-muted/50 transition-colors flex items-center gap-2 w-full md:w-auto justify-start md:justify-center"
          aria-label="Toggle theme"
          data-testid="theme-toggle"
        >
          {getThemeIcon()}
          {/* Visible label on md+ screens so it's clear on navbar */}
          <span className="hidden md:inline-block text-sm text-foreground/90">{getThemeLabel()}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-[140px]">
        <DropdownMenuItem
          onClick={() => setTheme('light')}
          className={`flex items-center gap-2 ${theme === 'light' ? 'bg-accent' : ''}`}
        >
          <Sun className="h-4 w-4" />
          <span>Light</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setTheme('dark')}
          className={`flex items-center gap-2 ${theme === 'dark' ? 'bg-accent' : ''}`}
        >
          <Moon className="h-4 w-4" />
          <span>Dark</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setTheme('system')}
          className={`flex items-center gap-2 ${theme === 'system' ? 'bg-accent' : ''}`}
        >
          <Monitor className="h-4 w-4" />
          <span>System</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}