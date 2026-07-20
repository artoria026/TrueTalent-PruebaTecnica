import { QueryClient } from '@tanstack/react-query';

const DEFAULT_STALE_TIME_MS = 10_000;
const DEFAULT_RETRY_COUNT = 1;

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: DEFAULT_STALE_TIME_MS,
      retry: DEFAULT_RETRY_COUNT,
      refetchOnWindowFocus: false,
    },
  },
});
