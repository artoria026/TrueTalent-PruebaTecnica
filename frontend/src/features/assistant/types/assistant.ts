export interface SummarizeTextPayload {
  user_id: string;
  text: string;
}

export interface SummarizeTextResponse {
  id: string;
  user_id: string;
  summary: string;
  model: string;
  created_at: string;
}

export interface AssistantLogEntry {
  id: string;
  user_id: string;
  prompt: string;
  summary: string | null;
  model: string;
  status: 'completed' | 'failed';
  created_at: string;
}

export interface AssistantLogListResponse {
  items: AssistantLogEntry[];
  total: number;
  page: number;
  limit: number;
}

export interface AssistantLogCreatedEvent {
  event: 'assistant.created';
  id: string;
  model: string;
}

export interface AiMode {
  force_mock: boolean;
}
