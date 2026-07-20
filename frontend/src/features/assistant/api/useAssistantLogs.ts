import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { fetchAssistantLogs } from '@/features/assistant/api/assistantApi';
import type { AssistantLogListResponse } from '@/features/assistant/types/assistant';

export const ASSISTANT_LOGS_QUERY_KEY = 'assistant-logs';

export function useAssistantLogs(
  page: number,
  limit: number,
): UseQueryResult<AssistantLogListResponse> {
  return useQuery({
    queryKey: [ASSISTANT_LOGS_QUERY_KEY, page, limit],
    queryFn: () => fetchAssistantLogs(page, limit),
  });
}
