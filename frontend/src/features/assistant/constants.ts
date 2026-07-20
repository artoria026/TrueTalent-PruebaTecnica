interface ModelDisplay {
  label: string;
  className: string;
}

const MOCK_MODEL_DISPLAY: ModelDisplay = {
  label: 'Simulado (sin IA real)',
  className: 'bg-surface-alt text-ink-faint',
};

const REAL_MODEL_CLASSES = 'bg-mod-assistant-soft text-mod-assistant';

export function getModelDisplay(model: string): ModelDisplay {
  if (model === 'mock') {
    return MOCK_MODEL_DISPLAY;
  }
  if (model.startsWith('gemini')) {
    return { label: `Gemini · ${model}`, className: REAL_MODEL_CLASSES };
  }
  if (model.startsWith('gpt') || model.startsWith('o1') || model.startsWith('o3')) {
    return { label: `OpenAI · ${model}`, className: REAL_MODEL_CLASSES };
  }
  return { label: model, className: REAL_MODEL_CLASSES };
}
