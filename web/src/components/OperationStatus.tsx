import type { Operation } from '../api/schema';
export function OperationStatus({ operations }: { operations: Operation[] }) {
  if (!operations.length)
    return <p className="muted">No write operations authorised.</p>;
  return (
    <ul className="operations">
      {operations.map((op) => (
        <li key={op.id}>
          <strong>
            {op.state === 'succeeded'
              ? op.ordinal === 1
                ? 'Ticket confirmed'
                : 'Order annotation confirmed'
              : op.state === 'unknown' || op.state === 'in_flight'
                ? 'Outcome unconfirmed'
                : op.state === 'rejected'
                  ? 'Write rejected'
                  : 'Awaiting execution'}
          </strong>
          <span>
            {op.kind.replaceAll('_', ' ')} / {op.attempts ?? 0} of 3 sends
          </span>
          {op.remote_id && <code>{op.remote_id}</code>}
          {op.last_error && <span className="warning">{op.last_error}</span>}
        </li>
      ))}
    </ul>
  );
}
