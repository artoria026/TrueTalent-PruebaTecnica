import { useTheme } from '@/shared/hooks/useTheme';

export function ThemeToggle(): JSX.Element {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      title={isDark ? 'Modo claro' : 'Modo oscuro'}
      className="flex h-7 w-7 items-center justify-center rounded border border-line bg-surface text-ink-muted transition-colors hover:text-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
    >
      {isDark ? (
        <svg viewBox="0 0 20 20" width="14" height="14" fill="currentColor" aria-hidden="true">
          <path d="M10 2.5a.75.75 0 0 1 .75.75V4.5a.75.75 0 0 1-1.5 0V3.25A.75.75 0 0 1 10 2.5Zm0 12.5a.75.75 0 0 1 .75.75v1.25a.75.75 0 0 1-1.5 0V15.75A.75.75 0 0 1 10 15Zm7.5-5a.75.75 0 0 1-.75.75H15.5a.75.75 0 0 1 0-1.5h1.25a.75.75 0 0 1 .75.75ZM4.5 10a.75.75 0 0 1-.75.75H2.5a.75.75 0 0 1 0-1.5h1.25A.75.75 0 0 1 4.5 10Zm10.44-5.94a.75.75 0 0 1 0 1.06l-.88.88a.75.75 0 1 1-1.06-1.06l.88-.88a.75.75 0 0 1 1.06 0ZM6 14.06a.75.75 0 0 1 0 1.06l-.88.88a.75.75 0 1 1-1.06-1.06l.88-.88a.75.75 0 0 1 1.06 0Zm8.88 1.94a.75.75 0 0 1-1.06 0l-.88-.88a.75.75 0 1 1 1.06-1.06l.88.88a.75.75 0 0 1 0 1.06ZM5.94 5.94a.75.75 0 0 1-1.06 0l-.88-.88a.75.75 0 0 1 1.06-1.06l.88.88a.75.75 0 0 1 0 1.06ZM10 6a4 4 0 1 1 0 8 4 4 0 0 1 0-8Z" />
        </svg>
      ) : (
        <svg viewBox="0 0 20 20" width="14" height="14" fill="currentColor" aria-hidden="true">
          <path d="M17.293 13.293a8 8 0 0 1-10.586-10.586 8.001 8.001 0 1 0 10.586 10.586Z" />
        </svg>
      )}
    </button>
  );
}
