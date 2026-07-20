import { apiClient } from '@/shared/lib/axios';
import type {
  CreateTransactionPayload,
  Transaction,
  TransactionListResponse,
} from '@/features/transactions/types/transaction';

export async function fetchTransactions(
  page: number,
  limit: number,
): Promise<TransactionListResponse> {
  const response = await apiClient.get<TransactionListResponse>('/transactions', {
    params: { page, limit },
  });
  return response.data;
}

export async function createTransaction(
  payload: CreateTransactionPayload,
): Promise<Transaction> {
  const response = await apiClient.post<Transaction>('/transactions/create', payload);
  return response.data;
}

export async function createTransactionAsync(
  payload: CreateTransactionPayload,
): Promise<Transaction> {
  const response = await apiClient.post<Transaction>(
    '/transactions/async-process',
    payload,
  );
  return response.data;
}
