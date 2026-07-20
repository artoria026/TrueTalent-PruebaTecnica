import { Badge } from '@/shared/components/Badge';
import type { Transaction } from '@/features/transactions/types/transaction';

interface TransactionCardProps {
  transaction: Transaction;
}

const CURRENCY_FORMATTER = new Intl.NumberFormat('es-ES', {
  style: 'currency',
  currency: 'USD',
});

export function TransactionCard({ transaction }: TransactionCardProps): JSX.Element {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-line bg-surface p-3.5">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-ink">{transaction.user_id}</p>
        <p className="text-xs text-ink-faint">
          {transaction.tipo} · {new Date(transaction.created_at).toLocaleString('es-ES')}
        </p>
      </div>
      <div className="flex shrink-0 flex-col items-end gap-1">
        <span className="font-display text-sm font-semibold tabular-nums text-ink">
          {CURRENCY_FORMATTER.format(transaction.monto)}
        </span>
        <Badge status={transaction.status} />
      </div>
    </div>
  );
}
