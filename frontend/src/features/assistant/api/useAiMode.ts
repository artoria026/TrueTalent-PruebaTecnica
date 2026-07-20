import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from '@tanstack/react-query';
import { fetchAiMode, updateAiMode } from '@/features/assistant/api/assistantApi';
import type { AiMode } from '@/features/assistant/types/assistant';

export const AI_MODE_QUERY_KEY = 'ai-mode';

export function useAiMode(): UseQueryResult<AiMode> {
  return useQuery({
    queryKey: [AI_MODE_QUERY_KEY],
    queryFn: fetchAiMode,
  });
}

export function useSetAiMode(): UseMutationResult<AiMode, Error, boolean> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateAiMode,
    onSuccess: (data) => {
      queryClient.setQueryData([AI_MODE_QUERY_KEY], data);
    },
  });
}
