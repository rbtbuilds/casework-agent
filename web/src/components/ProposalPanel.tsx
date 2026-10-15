import type { CaseView } from '../api/schema';
import { OperationStatus } from './OperationStatus';
export function ProposalPanel({
  active,
  pending,
  onAction,
}: {
  active: CaseView;
  pending: boolean;
  onAction: (
    action: 'approve' | 'reject' | 'cancel' | 'repropose' | 'reconcile',
  ) => void;
}) {
  const p = active.proposal;
  const expired = !!p && Date.parse(p.expires_at) <= Date.now();
  return (
    <aside className="proposal panel" aria-labelledby="proposal-heading">
      <div className="section-label">03 / Decision</div>
      <h2 id="proposal-heading">Human approval</h2>
      {p ? (
        <>
          <p className="action-name">{p.action.replaceAll('_', ' ')}</p>
          <p>{p.rationale}</p>
          <h3>Exact internal note</h3>
          <blockquote>{p.draft_note}</blockquote>
          <dl>
            <dt>Ticket queue</dt>
            <dd>{p.intents[0]?.queue.replaceAll('_', ' ')}</dd>
            <dt>Priority</dt>
            <dd>Normal</dd>
            <dt>Approved source versions</dt>
            <dd>
              Order v{p.order_version} / carrier v{p.shipment_version}
            </dd>
            <dt>Proposal</dt>
            <dd>Version {p.version}</dd>
            <dt>Expires</dt>
            <dd>
              <time dateTime={p.expires_at}>
                {new Date(p.expires_at).toLocaleString()}
              </time>
              {expired && ' / Expired'}
            </dd>
            <dt>Exact proposal hash</dt>
            <dd>
              <code>{p.hash}</code>
            </dd>
          </dl>
          <p className="muted">
            Approval permits one fictional ticket and one order annotation,
            using the note above.
          </p>
          {active.available_actions?.includes('approve') && !expired && (
            <div className="action-stack">
              <button
                className="primary"
                disabled={pending}
                onClick={() => onAction('approve')}
              >
                Approve fictional action
              </button>
              <button disabled={pending} onClick={() => onAction('reject')}>
                Reject proposal
              </button>
            </div>
          )}
        </>
      ) : (
        <p className="muted">
          The agent must read the order, carrier and policy before a proposal
          can appear.
        </p>
      )}
      <div className="secondary-actions">
        {active.available_actions
          ?.filter((a) => a !== 'approve' && a !== 'reject')
          .map((action) => (
            <button
              key={action}
              disabled={pending}
              onClick={() => onAction(action)}
            >
              {action === 'cancel'
                ? 'Cancel before execution'
                : action === 'repropose'
                  ? 'Gather a new proposal'
                  : 'Reconcile uncertain outcome'}
            </button>
          ))}
      </div>
      {!!active.operations?.some((o) => (o.attempts ?? 0) > 0) && (
        <p className="muted">
          Execution started; reconciliation may still be required.
        </p>
      )}
      <h3>Write outcomes</h3>
      <OperationStatus operations={active.operations ?? []} />
    </aside>
  );
}
