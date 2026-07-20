import { TRANSACTION_STATUS_LABELS } from '@/features/transactions/constants';
import type { TransactionStatus } from '@/features/transactions/types/transaction';

interface BadgeProps {
  status: TransactionStatus;
}

const STATUS_TEXT_CLASSES: Record<TransactionStatus, string> = {
  pending: 'text-warning',
  processed: 'text-success',
  failed: 'text-danger',
};

const STATUS_DOT_CLASSES: Record<TransactionStatus, string> = {
  pending: 'bg-warning shadow-[0_0_0_3px_rgba(224,169,77,0.2)]',
  processed: 'bg-success shadow-[0_0_0_3px_rgba(121,192,138,0.2)]',
  failed: 'bg-danger',
};

export function Badge({ status }: BadgeProps): JSX.Element {
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-medium ${STATUS_TEXT_CLASSES[status]}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT_CLASSES[status]}`} />
      {TRANSACTION_STATUS_LABELS[status]}
    </span>
  );
}
