export type TransactionStatus = 'pending' | 'processed' | 'failed';

export type TransactionType = 'deposito' | 'retiro' | 'transferencia';

export interface Transaction {
  id: string;
  user_id: string;
  monto: number;
  tipo: TransactionType;
  status: TransactionStatus;
  idempotency_key: string;
  created_at: string;
  processed_at: string | null;
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  page: number;
  limit: number;
}

export interface CreateTransactionPayload {
  user_id: string;
  monto: number;
  tipo: TransactionType;
  idempotency_key: string;
}

export interface TransactionUpdatedEvent {
  event: 'transaction.updated';
  id: string;
  status: TransactionStatus;
}
