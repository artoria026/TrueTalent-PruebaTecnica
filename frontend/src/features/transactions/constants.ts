import type { TransactionStatus } from '@/features/transactions/types/transaction';

export const TRANSACTION_STATUS_LABELS: Record<TransactionStatus, string> = {
  pending: 'Pendiente',
  processed: 'Procesada',
  failed: 'Fallida',
};
