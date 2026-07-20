import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { fetchTransactions } from '@/features/transactions/api/transactionsApi';
import type { TransactionListResponse } from '@/features/transactions/types/transaction';

export const TRANSACTIONS_QUERY_KEY = 'transactions';

export function useTransactions(
  page: number,
  limit: number,
): UseQueryResult<TransactionListResponse> {
  return useQuery({
    queryKey: [TRANSACTIONS_QUERY_KEY, page, limit],
    queryFn: () => fetchTransactions(page, limit),
  });
}
