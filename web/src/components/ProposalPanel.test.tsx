import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { ProposalPanel } from './ProposalPanel';
import { readyCase } from '../test/fixtures';
it('shows the exact note and hash before allowing approval', async () => {
  const onAction = vi.fn();
  render(
    <ProposalPanel active={readyCase} pending={false} onAction={onAction} />,
  );
  expect(screen.getByText('Fictional internal note.')).toBeVisible();
  expect(screen.getByText('a'.repeat(64))).toBeVisible();
  await userEvent.click(
    screen.getByRole('button', { name: 'Approve fictional action' }),
  );
  expect(onAction).toHaveBeenCalledWith('approve');
  await userEvent.click(
    screen.getByRole('button', { name: 'Reject proposal' }),
  );
  expect(onAction).toHaveBeenCalledWith('reject');
});
it('blocks duplicate clicks while a decision is pending', async () => {
  const onAction = vi.fn();
  render(<ProposalPanel active={readyCase} pending onAction={onAction} />);
  await userEvent.click(
    screen.getByRole('button', { name: 'Approve fictional action' }),
  );
  expect(onAction).not.toHaveBeenCalled();
});
it('removes approval when the server invalidates the proposal', () => {
  render(
    <ProposalPanel
      active={{
        ...readyCase,
        state: 'stale',
        available_actions: ['repropose'],
      }}
      pending={false}
      onAction={vi.fn()}
    />,
  );
  expect(
    screen.queryByRole('button', { name: 'Approve fictional action' }),
  ).not.toBeInTheDocument();
  expect(
    screen.getByRole('button', { name: 'Gather a new proposal' }),
  ).toBeEnabled();
});
it('never offers an expired proposal for approval', () => {
  render(
    <ProposalPanel
      active={{
        ...readyCase,
        proposal: { ...readyCase.proposal, expires_at: '2000-01-01T00:00:00Z' },
      }}
      pending={false}
      onAction={vi.fn()}
    />,
  );
  expect(
    screen.queryByRole('button', { name: 'Approve fictional action' }),
  ).not.toBeInTheDocument();
});
