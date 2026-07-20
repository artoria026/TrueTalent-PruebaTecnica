import { useAiMode, useSetAiMode } from '@/features/assistant/api/useAiMode';

export function AiModeToggle(): JSX.Element | null {
  const { data, isLoading } = useAiMode();
  const setAiMode = useSetAiMode();

  if (isLoading || data === undefined) {
    return null;
  }

  // Optimistic value while the toggle round-trips.
  const forceMock = setAiMode.isPending ? (setAiMode.variables ?? data.force_mock) : data.force_mock;

  const handleToggle = (): void => {
    setAiMode.mutate(!forceMock);
  };

  return (
    <button
      type="button"
      role="switch"
      aria-checked={forceMock}
      onClick={handleToggle}
      disabled={setAiMode.isPending}
      title="Compartido con el RPA: al simular aquí, el RPA también simula en su próxima corrida."
      className="flex items-center gap-2 rounded-full border border-line bg-surface px-2.5 py-1 text-xs font-medium text-ink-muted transition-colors hover:text-ink disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
    >
      <span
        aria-hidden="true"
        className={`relative inline-flex h-4 w-7 shrink-0 items-center rounded-full transition-colors ${
          forceMock ? 'bg-ink-faint' : 'bg-mod-assistant'
        }`}
      >
        <span
          className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
            forceMock ? 'translate-x-0.5' : 'translate-x-3.5'
          }`}
        />
      </span>
      {forceMock ? 'Simulando (ahorra tokens)' : 'IA real activa'}
    </button>
  );
}
