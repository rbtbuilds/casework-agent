import { act, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import App from './App';
import { api } from './api/client';
import type { CaseView } from './api/schema';
import { readyCase } from './test/fixtures';

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: Error) => void;
  const promise = new Promise<T>((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { promise, resolve, reject };
}
const a: CaseView = { ...readyCase, id: 'a', order_id: 'order-a' };
const b: CaseView = { ...readyCase, id: 'b', order_id: 'order-b' };
beforeEach(() => {
  vi.spyOn(api, 'listScenarios').mockResolvedValue([]);
  vi.spyOn(api, 'listCases').mockResolvedValue([a, b]);
});
afterEach(() => vi.restoreAllMocks());

it('keeps the most recently selected case when requests finish out of order', async () => {
  const first = deferred<CaseView>(),
    second = deferred<CaseView>();
  vi.spyOn(api, 'getCase').mockImplementation((id) =>
    id === 'a' ? first.promise : second.promise,
  );
  render(<App />);
  fireEvent.click(await screen.findByRole('button', { name: /order-a/ }));
  fireEvent.click(screen.getByRole('button', { name: /order-b/ }));
  await act(async () => second.resolve(b));
  expect(screen.getByRole('heading', { name: 'Order order-b' })).toBeVisible();
  await act(async () => first.resolve(a));
  expect(screen.getByRole('heading', { name: 'Order order-b' })).toBeVisible();
});

it('ignores an older poll after a newer mutation response', async () => {
  let poll: (() => void) | undefined;
  const interval = globalThis.setInterval.bind(globalThis);
  vi.spyOn(window, 'setInterval').mockImplementation((handler) => {
    if (typeof handler === 'function') poll = () => handler();
    return interval(() => {}, 60000);
  });
  const old = deferred<CaseView>();
  vi.spyOn(api, 'getCase')
    .mockResolvedValueOnce(a)
    .mockReturnValueOnce(old.promise);
  vi.spyOn(api, 'decide').mockResolvedValue({
    ...a,
    version: 4,
    state: 'approved',
    available_actions: [],
  });
  render(<App />);
  fireEvent.click(await screen.findByRole('button', { name: /order-a/ }));
  await screen.findByRole('heading', { name: 'Order order-a' });
  act(() => poll?.());
  fireEvent.click(
    screen.getByRole('button', { name: 'Approve fictional action' }),
  );
  await screen.findByText('Case version 4');
  await act(async () => old.resolve(a));
  expect(screen.getByText('Case version 4')).toBeVisible();
  expect(
    screen.queryByRole('button', { name: 'Approve fictional action' }),
  ).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: /order-a/ })).toHaveTextContent(
    'approved',
  );
});

it('keeps a failed mutation retry available after another selection', async () => {
  vi.spyOn(api, 'getCase').mockImplementation(async (id) =>
    id === 'a' ? a : b,
  );
  const decision = vi
    .spyOn(api, 'decide')
    .mockRejectedValueOnce(new Error('Response lost.'))
    .mockResolvedValueOnce({
      ...a,
      version: 4,
      state: 'approved',
      available_actions: [],
    });
  render(<App />);
  fireEvent.click(await screen.findByRole('button', { name: /order-a/ }));
  fireEvent.click(
    await screen.findByRole('button', { name: 'Approve fictional action' }),
  );
  await screen.findByRole('button', { name: 'Retry saved request' });
  fireEvent.click(screen.getByRole('button', { name: /order-b/ }));
  await screen.findByRole('heading', { name: 'Order order-b' });
  fireEvent.click(screen.getByRole('button', { name: 'Retry saved request' }));
  await screen.findByText('Case version 4');
  expect(decision.mock.calls[1]).toEqual(decision.mock.calls[0]);
});
