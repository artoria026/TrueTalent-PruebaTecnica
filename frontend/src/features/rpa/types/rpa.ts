export interface RpaExtractionEntry {
  id: string;
  term: string;
  paragraph: string;
  source_url: string;
  created_at: string;
}

export interface RpaExtractionListResponse {
  items: RpaExtractionEntry[];
  total: number;
  page: number;
  limit: number;
}

export interface RpaExtractedEvent {
  event: 'rpa.extracted';
  id: string;
  term: string;
}
