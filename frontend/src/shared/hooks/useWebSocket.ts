import { useCallback, useEffect, useRef, useState } from 'react';

const DEFAULT_RECONNECT_INTERVAL_MS = 3000;

interface UseWebSocketOptions {
  onMessage: (data: unknown) => void;
  reconnectInterval?: number;
}

export function useWebSocket(url: string, options: UseWebSocketOptions): boolean {
  const { onMessage, reconnectInterval = DEFAULT_RECONNECT_INTERVAL_MS } = options;
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const isUnmountedRef = useRef(false);
  const [isConnected, setIsConnected] = useState(false);

  const connect = useCallback(() => {
    const socket = new WebSocket(url);
    wsRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
    };

    socket.onmessage = (event: MessageEvent<string>) => {
      try {
        const data: unknown = JSON.parse(event.data);
        onMessage(data);
      } catch {
        // Malformed message from the server: ignore silently.
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      if (!isUnmountedRef.current) {
        reconnectTimerRef.current = setTimeout(connect, reconnectInterval);
      }
    };
  }, [url, onMessage, reconnectInterval]);

  useEffect(() => {
    isUnmountedRef.current = false;
    connect();

    return () => {
      isUnmountedRef.current = true;
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return isConnected;
}
