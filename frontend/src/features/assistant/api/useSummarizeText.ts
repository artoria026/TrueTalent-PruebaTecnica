import { useMutation, useQueryClient, type UseMutationResult } from '@tanstack/react-query';
import { summarizeText } from '@/features/assistant/api/assistantApi';
import { ASSISTANT_LOGS_QUERY_KEY } from '@/features/assistant/api/useAssistantLogs';
import type {
  SummarizeTextPayload,
  SummarizeTextResponse,
} from '@/features/assistant/types/assistant';

export function useSummarizeText(): UseMutationResult<
  SummarizeTextResponse,
  Error,
  SummarizeTextPayload
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: summarizeText,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [ASSISTANT_LOGS_QUERY_KEY] });
    },
  });
}
