interface ConnectionPulseProps {
  connected: boolean;
}

export function ConnectionPulse({ connected }: ConnectionPulseProps): JSX.Element {
  return (
    <span className="inline-flex items-center gap-2 text-xs font-medium text-ink-muted">
      <span className="relative inline-flex h-2 w-2">
        {connected && (
          <span className="absolute inset-0 -m-1 animate-led-ping rounded-full border border-success motion-reduce:hidden" />
        )}
        <span
          className={`relative h-2 w-2 rounded-full ${connected ? 'bg-success' : 'bg-ink-faint'}`}
        />
      </span>
      {connected ? 'WebSocket conectado' : 'Reconectando…'}
    </span>
  );
}
