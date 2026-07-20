import { useState } from 'react';
import { useTransactions } from '@/features/transactions/api/useTransactions';
import { TransactionCard } from '@/features/transactions/components/TransactionCard';
import { Button } from '@/shared/components/Button';

const DEFAULT_PAGE_LIMIT = 10;
const FIRST_PAGE = 1;

export function TransactionList(): JSX.Element {
  const [page, setPage] = useState(FIRST_PAGE);
  const { data, isLoading, isError } = useTransactions(page, DEFAULT_PAGE_LIMIT);

  if (isLoading) {
    return <p className="text-sm text-ink-faint">Cargando transacciones…</p>;
  }

  if (isError || !data) {
    return <p className="text-sm text-danger">No se pudieron cargar las transacciones.</p>;
  }

  const totalPages = Math.max(1, Math.ceil(data.total / data.limit));

  return (
    <div className="flex flex-col gap-3">
      {data.items.length === 0 ? (
        <p className="text-sm text-ink-faint">Aún no hay transacciones.</p>
      ) : (
        data.items.map((transaction) => (
          <TransactionCard key={transaction.id} transaction={transaction} />
        ))
      )}

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
    </div>
  );
}
