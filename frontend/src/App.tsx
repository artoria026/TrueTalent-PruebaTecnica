import { useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from '@/shared/hooks/useWebSocket';
import { useToast } from '@/shared/components/ToastProvider';
import { ConnectionPulse } from '@/shared/components/ConnectionPulse';
import { ThemeToggle } from '@/shared/components/ThemeToggle';
import { TRANSACTIONS_QUERY_KEY, useTransactions } from '@/features/transactions/api/useTransactions';
import { TransactionForm } from '@/features/transactions/components/TransactionForm';
import { TransactionList } from '@/features/transactions/components/TransactionList';
import { AiModeToggle } from '@/features/assistant/components/AiModeToggle';
import { SummarizeForm } from '@/features/assistant/components/SummarizeForm';
import { AssistantHistoryList } from '@/features/assistant/components/AssistantHistoryList';
import {
  ASSISTANT_LOGS_QUERY_KEY,
  useAssistantLogs,
} from '@/features/assistant/api/useAssistantLogs';
import { getModelDisplay } from '@/features/assistant/constants';
import { RpaExtractionsList } from '@/features/rpa/components/RpaExtractionsList';
import {
  RPA_EXTRACTIONS_QUERY_KEY,
  useRpaExtractions,
} from '@/features/rpa/api/useRpaExtractions';
import { TRANSACTION_STATUS_LABELS } from '@/features/transactions/constants';
import type { TransactionUpdatedEvent } from '@/features/transactions/types/transaction';
import type { AssistantLogCreatedEvent } from '@/features/assistant/types/assistant';
import type { RpaExtractedEvent } from '@/features/rpa/types/rpa';

// Derived from the page origin so it works on any host/port, like axios.ts.
const DEFAULT_WS_URL = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/v1/transactions/stream`;
const WS_URL: string = import.meta.env.VITE_WS_URL ?? DEFAULT_WS_URL;

// Same query key as each list's page-1 request, so React Query dedupes.
const KPI_PAGE = 1;
const KPI_LIMIT = 1;

function isTransactionUpdatedEvent(data: unknown): data is TransactionUpdatedEvent {
  return (
    typeof data === 'object' &&
    data !== null &&
    'event' in data &&
    (data as { event: unknown }).event === 'transaction.updated'
  );
}

function isAssistantCreatedEvent(data: unknown): data is AssistantLogCreatedEvent {
  return (
    typeof data === 'object' &&
    data !== null &&
    'event' in data &&
    (data as { event: unknown }).event === 'assistant.created'
  );
}

function isRpaExtractedEvent(data: unknown): data is RpaExtractedEvent {
  return (
    typeof data === 'object' &&
    data !== null &&
    'event' in data &&
    (data as { event: unknown }).event === 'rpa.extracted'
  );
}

export default function App(): JSX.Element {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const handleMessage = useCallback(
    (data: unknown) => {
      if (isTransactionUpdatedEvent(data)) {
        void queryClient.invalidateQueries({ queryKey: [TRANSACTIONS_QUERY_KEY] });
        const statusLabel = TRANSACTION_STATUS_LABELS[data.status];
        showToast(`Transacción ${data.id.slice(0, 8)} → ${statusLabel}`, 'info');
        return;
      }
      if (isAssistantCreatedEvent(data)) {
        void queryClient.invalidateQueries({ queryKey: [ASSISTANT_LOGS_QUERY_KEY] });
        const { label } = getModelDisplay(data.model);
        showToast(`Nuevo resumen generado · ${label}`, 'info');
        return;
      }
      if (isRpaExtractedEvent(data)) {
        void queryClient.invalidateQueries({ queryKey: [RPA_EXTRACTIONS_QUERY_KEY] });
        showToast(`RPA extrajo contenido de Wikipedia · "${data.term}"`, 'info');
      }
    },
    [queryClient, showToast],
  );

  const isConnected = useWebSocket(WS_URL, { onMessage: handleMessage });

  const transactionsTotal = useTransactions(KPI_PAGE, KPI_LIMIT).data?.total;
  const assistantTotal = useAssistantLogs(KPI_PAGE, KPI_LIMIT).data?.total;
  const rpaTotal = useRpaExtractions(KPI_PAGE, KPI_LIMIT).data?.total;

  return (
    <div className="min-h-screen bg-bg font-sans text-ink">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-line pb-6">
          <div>
            <h1 className="font-display text-2xl font-bold text-ink">Panel de Transacciones</h1>
            <p className="text-sm text-ink-muted">
              Creación idempotente, procesamiento asíncrono y notificaciones en tiempo real.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <ConnectionPulse connected={isConnected} />
            <ThemeToggle />
          </div>
        </header>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          <KpiTile label="Transacciones" value={transactionsTotal} dotClassName="bg-mod-transactions" />
          <KpiTile label="Resúmenes IA" value={assistantTotal} dotClassName="bg-mod-assistant" />
          <KpiTile label="Extracciones RPA" value={rpaTotal} dotClassName="bg-mod-rpa" />
        </div>

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-3">
          <section className="flex flex-col gap-4 rounded-xl border border-line bg-surface-alt p-4">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-mod-transactions" />
              <h2 className="font-display text-base font-semibold text-ink">Transacciones</h2>
            </div>
            <TransactionForm />
            <TransactionList />
          </section>

          <section className="flex flex-col gap-4 rounded-xl border border-line bg-surface-alt p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-mod-assistant" />
                <h2 className="font-display text-base font-semibold text-ink">Asistente IA</h2>
              </div>
              <AiModeToggle />
            </div>
            <SummarizeForm />
            <div className="flex flex-col gap-2">
              <h3 className="text-xs font-medium uppercase tracking-wide text-ink-faint">
                Historial
              </h3>
              <AssistantHistoryList />
            </div>
          </section>

          <section className="flex flex-col gap-4 rounded-xl border border-line bg-surface-alt p-4">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-mod-rpa" />
              <h2 className="font-display text-base font-semibold text-ink">RPA Wikipedia</h2>
            </div>
            <RpaExtractionsList />
          </section>
        </div>

        <footer className="border-t border-line pt-6 text-center text-sm text-ink-faint">
          Prueba técnica para True Talent — Arturo Chavira
        </footer>
      </div>
    </div>
  );
}

interface KpiTileProps {
  label: string;
  value: number | undefined;
  dotClassName: string;
}

function KpiTile({ label, value, dotClassName }: KpiTileProps): JSX.Element {
  return (
    <div className="rounded-xl border border-line bg-surface p-4">
      <div className="flex items-center gap-2">
        <span className={`h-1.5 w-1.5 rounded-full ${dotClassName}`} />
        <p className="text-xs font-medium uppercase tracking-wide text-ink-faint">{label}</p>
      </div>
      <p className="mt-2 font-display text-2xl font-extrabold tabular-nums text-ink">
        {value ?? '—'}
      </p>
    </div>
  );
}
