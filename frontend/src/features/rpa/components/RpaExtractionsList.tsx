import { useState } from 'react';
import { useRpaExtractions } from '@/features/rpa/api/useRpaExtractions';
import type { RpaExtractionEntry } from '@/features/rpa/types/rpa';
import { Button } from '@/shared/components/Button';

const DEFAULT_PAGE_LIMIT = 5;
const FIRST_PAGE = 1;

export function RpaExtractionsList(): JSX.Element {
  const [page, setPage] = useState(FIRST_PAGE);
  const { data, isLoading, isError } = useRpaExtractions(page, DEFAULT_PAGE_LIMIT);

  if (isLoading) {
    return <p className="text-sm text-ink-faint">Cargando extracciones…</p>;
  }

  if (isError || !data) {
    return <p className="text-sm text-danger">No se pudieron cargar las extracciones.</p>;
  }

  const totalPages = Math.max(1, Math.ceil(data.total / data.limit));

  return (
    <div className="flex flex-col gap-3">
      {data.items.length === 0 ? (
        <p className="text-sm text-ink-faint">Aún no hay extracciones del RPA.</p>
      ) : (
        data.items.map((entry) => <RpaExtractionCard key={entry.id} entry={entry} />)
      )}

      {data.items.length > 0 && (
        <div className="flex items-center justify-between pt-2">
          <Button
            variant="secondary"
            disabled={page <= FIRST_PAGE}
            onClick={() => setPage((prev) => prev - 1)}
          >
            Anterior
          </Button>
          <span className="text-xs text-ink-faint">
            Página {page} de {totalPages}
          </span>
          <Button
            variant="secondary"
            disabled={page >= totalPages}
            onClick={() => setPage((prev) => prev + 1)}
          >
            Siguiente
          </Button>
        </div>
      )}
    </div>
  );
}

function RpaExtractionCard({ entry }: { entry: RpaExtractionEntry }): JSX.Element {
  return (
    <div className="flex animate-fade-in flex-col gap-1.5 rounded-lg border border-line bg-surface p-3">
      <div className="flex items-center justify-between gap-2">
        <span className="inline-block w-fit rounded-full bg-mod-rpa-soft px-2.5 py-0.5 text-xs font-semibold text-mod-rpa">
          {entry.term}
        </span>
        <span className="shrink-0 text-xs text-ink-faint">
          {new Date(entry.created_at).toLocaleString('es-ES')}
        </span>
      </div>
      <p className="line-clamp-3 text-sm text-ink">{entry.paragraph}</p>
      <a
        href={entry.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="w-fit text-xs text-mod-rpa hover:underline"
      >
        Ver fuente original ↗
      </a>
    </div>
  );
}
