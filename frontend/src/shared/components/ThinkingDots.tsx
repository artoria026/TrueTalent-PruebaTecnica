export function ThinkingDots(): JSX.Element {
  return (
    <span className="inline-flex items-center gap-1" role="status" aria-label="Generando…">
      <span className="h-2 w-2 animate-dot-pulse rounded-full bg-current [animation-delay:0ms]" />
      <span className="h-2 w-2 animate-dot-pulse rounded-full bg-current [animation-delay:150ms]" />
      <span className="h-2 w-2 animate-dot-pulse rounded-full bg-current [animation-delay:300ms]" />
    </span>
  );
}
