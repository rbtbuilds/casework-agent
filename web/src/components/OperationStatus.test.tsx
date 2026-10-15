import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { OperationStatus } from './OperationStatus';
import type { Operation } from '../api/schema';
it('keeps an uncertain write visible', () => {
  const operation = {
    id: 'op',
    case_id: 'case',
    approval_id: 'approval',
    ordinal: 1,
    kind: 'create_ticket',
    key: 'key',
    state: 'unknown',
    attempts: 1,
    worker_generation: 1,
    last_error: null,
    remote_id: null,
    request_hash: null,
    request_json: null,
    response_json: null,
  } satisfies Operation;
  render(<OperationStatus operations={[operation]} />);
  expect(screen.getByText('Outcome unconfirmed')).toBeVisible();
  expect(screen.queryByText('Completed')).not.toBeInTheDocument();
});
