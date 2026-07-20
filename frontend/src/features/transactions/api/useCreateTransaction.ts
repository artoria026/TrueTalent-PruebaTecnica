import { useMutation, useQueryClient, type UseMutationResult } from '@tanstack/react-query';
import {
  createTransaction,
  createTransactionAsync,
} from '@/features/transactions/api/transactionsApi';
import { TRANSACTIONS_QUERY_KEY } from '@/features/transactions/api/useTransactions';
import type {
  CreateTransactionPayload,
  Transaction,
} from '@/features/transactions/types/transaction';

export function useCreateTransaction(): UseMutationResult<
  Transaction,
  Error,
  CreateTransactionPayload
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTransaction,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [TRANSACTIONS_QUERY_KEY] });
    },
  });
}

export function useCreateTransactionAsync(): UseMutationResult<
  Transaction,
  Error,
  CreateTransactionPayload
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTransactionAsync,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [TRANSACTIONS_QUERY_KEY] });
    },
  });
}
