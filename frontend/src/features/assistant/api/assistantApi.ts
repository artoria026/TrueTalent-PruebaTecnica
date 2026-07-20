import { apiClient } from '@/shared/lib/axios';
import type {
  AiMode,
  AssistantLogListResponse,
  SummarizeTextPayload,
  SummarizeTextResponse,
} from '@/features/assistant/types/assistant';

export async function summarizeText(
  payload: SummarizeTextPayload,
): Promise<SummarizeTextResponse> {
  const response = await apiClient.post<SummarizeTextResponse>(
    '/assistant/summarize',
    payload,
  );
  return response.data;
}

export async function fetchAssistantLogs(
  page: number,
  limit: number,
): Promise<AssistantLogListResponse> {
  const response = await apiClient.get<AssistantLogListResponse>('/assistant/logs', {
    params: { page, limit },
  });
  return response.data;
}

export async function fetchAiMode(): Promise<AiMode> {
  const response = await apiClient.get<AiMode>('/assistant/ai-mode');
  return response.data;
}

export async function updateAiMode(forceMock: boolean): Promise<AiMode> {
  const response = await apiClient.put<AiMode>('/assistant/ai-mode', {
    force_mock: forceMock,
  });
  return response.data;
}
