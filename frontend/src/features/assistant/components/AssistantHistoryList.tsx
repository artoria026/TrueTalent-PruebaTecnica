import { useState } from 'react';
import { useAssistantLogs } from '@/features/assistant/api/useAssistantLogs';
import { getModelDisplay } from '@/features/assistant/constants';
import type { AssistantLogEntry } from '@/features/assistant/types/assistant';
import { Button } from '@/shared/components/Button';

const DEFAULT_PAGE_LIMIT = 5;
const FIRST_PAGE = 1;

export function AssistantHistoryList(): JSX.Element {
  const [page, setPage] = useState(FIRST_PAGE);
  const { data, isLoading, isError } = useAssistantLogs(page, DEFAULT_PAGE_LIMIT);

  if (isLoading) {
    return <p className="text-sm text-ink-faint">Cargando historial…</p>;
  }

  if (isError || !data) {
    return <p className="text-sm text-danger">No se pudo cargar el historial.</p>;
  }

  const totalPages = Math.max(1, Math.ceil(data.total / data.limit));

  return (
    <div className="flex flex-col gap-3">
      {data.items.length === 0 ? (
        <p className="text-sm text-ink-faint">
          Aún no hay resúmenes generados (desde el formulario o Postman).
        </p>
      ) : (
        data.items.map((entry) => <AssistantLogCard key={entry.id} entry={entry} />)
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

function AssistantLogCard({ entry }: { entry: AssistantLogEntry }): JSX.Element {
  const isFailed = entry.status === 'failed';
  const { label, className } = isFailed
    ? { label: 'Falló la IA', className: 'bg-danger-soft text-danger' }
    : getModelDisplay(entry.model);

  return (
    <div
      className={`flex animate-fade-in flex-col gap-1.5 rounded-lg border p-3 ${
        isFailed ? 'border-danger-line bg-danger-wash' : 'border-line bg-surface'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <span
          className={`inline-block w-fit rounded-full px-2.5 py-0.5 text-xs font-semibold ${className}`}
        >
          {label}
        </span>
        <span className="shrink-0 text-xs text-ink-faint">
          {new Date(entry.created_at).toLocaleString('es-ES')}
        </span>
      </div>
      {isFailed ? (
        <p className="text-sm italic text-ink-muted">
          No se pudo generar el resumen (falló el proveedor de IA), pero el intento
          quedó registrado.
        </p>
      ) : (
        <p className="text-sm text-ink">{entry.summary}</p>
      )}
    </div>
  );
}
