import { useState, type FormEvent } from 'react';
import axios from 'axios';
import { Button } from '@/shared/components/Button';
import { ThinkingDots } from '@/shared/components/ThinkingDots';
import { useToast } from '@/shared/components/ToastProvider';
import { useSummarizeText } from '@/features/assistant/api/useSummarizeText';
import { getModelDisplay } from '@/features/assistant/constants';

const DEFAULT_USER_ID = 'user-demo';
const TEXTAREA_ROWS = 5;

interface ApiErrorBody {
  code?: string;
  message?: string;
  retry_after_seconds?: number;
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const apiError = error.response?.data?.error as ApiErrorBody | undefined;
    if (apiError?.code === 'AI_QUOTA_EXCEEDED') {
      const retrySeconds = apiError.retry_after_seconds;
      const retryText =
        retrySeconds !== undefined ? ` Reintenta en ~${Math.ceil(retrySeconds)}s.` : '';
      return `Se agotó la cuota gratuita del proveedor de IA.${retryText}`;
    }
    if (apiError?.message !== undefined) {
      return apiError.message;
    }
  }
  return 'Error al generar el resumen';
}

export function SummarizeForm(): JSX.Element {
  const [text, setText] = useState('');
  const { showToast } = useToast();
  const summarize = useSummarizeText();
  const isLoading = summarize.isPending;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    try {
      await summarize.mutateAsync({ user_id: DEFAULT_USER_ID, text });
    } catch (error) {
      showToast(getErrorMessage(error), 'error');
    }
  };

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-line bg-surface p-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <label htmlFor="assistant-text" className="text-xs font-medium text-ink-muted">
          Texto a resumir
        </label>
        <textarea
          id="assistant-text"
          rows={TEXTAREA_ROWS}
          value={text}
          onChange={(event) => setText(event.target.value)}
          className="rounded-lg border border-line bg-bg px-3 py-2 text-sm text-ink transition-colors focus:outline-none focus:ring-2 focus:ring-accent disabled:text-ink-faint"
          disabled={isLoading}
          required
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              Generando
              <ThinkingDots />
            </span>
          ) : (
            'Resumir'
          )}
        </Button>
      </form>

      {!isLoading && summarize.data !== undefined && (
        <div className="flex animate-fade-in flex-col gap-2 rounded-lg bg-surface-alt p-3 text-sm text-ink">
          <ModelBadge model={summarize.data.model} />
          <p>{summarize.data.summary}</p>
        </div>
      )}
    </div>
  );
}

function ModelBadge({ model }: { model: string }): JSX.Element {
  const { label, className } = getModelDisplay(model);
  return (
    <span
      className={`inline-block w-fit rounded-full px-2.5 py-0.5 text-xs font-semibold ${className}`}
    >
      {label}
    </span>
  );
}
