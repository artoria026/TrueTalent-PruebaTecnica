import { useState, type FormEvent } from 'react';
import { Button } from '@/shared/components/Button';
import { Input } from '@/shared/components/Input';
import { Select } from '@/shared/components/Select';
import { useToast } from '@/shared/components/ToastProvider';
import {
  useCreateTransaction,
  useCreateTransactionAsync,
} from '@/features/transactions/api/useCreateTransaction';
import type { TransactionType } from '@/features/transactions/types/transaction';

const TRANSACTION_TYPE_OPTIONS: { value: TransactionType; label: string }[] = [
  { value: 'deposito', label: 'Depósito' },
  { value: 'retiro', label: 'Retiro' },
  { value: 'transferencia', label: 'Transferencia' },
];

const DEFAULT_USER_ID = 'user-demo';

export function TransactionForm(): JSX.Element {
  const [userId, setUserId] = useState(DEFAULT_USER_ID);
  const [monto, setMonto] = useState('');
  const [tipo, setTipo] = useState<TransactionType>('deposito');

  const { showToast } = useToast();
  const createTransaction = useCreateTransaction();
  const createTransactionAsync = useCreateTransactionAsync();

  const buildPayload = () => ({
    user_id: userId,
    monto: Number(monto),
    tipo,
    idempotency_key: crypto.randomUUID(),
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    try {
      await createTransaction.mutateAsync(buildPayload());
      showToast('Transacción creada correctamente', 'success');
      setMonto('');
    } catch {
      showToast('Error al crear la transacción', 'error');
    }
  };

  const handleAsyncSubmit = async (): Promise<void> => {
    try {
      await createTransactionAsync.mutateAsync(buildPayload());
      showToast('Transacción encolada para procesamiento', 'info');
      setMonto('');
    } catch {
      showToast('Error al encolar la transacción', 'error');
    }
  };

  const isSubmitting = createTransaction.isPending || createTransactionAsync.isPending;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 rounded-lg border border-line bg-surface p-4">
      <Input
        id="user_id"
        label="Usuario"
        value={userId}
        onChange={(event) => setUserId(event.target.value)}
        required
      />
      <Input
        id="monto"
        label="Monto"
        type="number"
        min="0.01"
        step="0.01"
        value={monto}
        onChange={(event) => setMonto(event.target.value)}
        required
      />
      <Select
        id="tipo"
        label="Tipo"
        value={tipo}
        onChange={(event) => setTipo(event.target.value as TransactionType)}
        options={TRANSACTION_TYPE_OPTIONS}
      />
      <div className="flex gap-3">
        <Button type="submit" disabled={isSubmitting}>
          Crear
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={isSubmitting}
          onClick={() => void handleAsyncSubmit()}
        >
          Procesar asíncronamente
        </Button>
      </div>
    </form>
  );
}
