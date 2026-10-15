import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from './api/client';
import type { ApprovalRequest, CaseView, Scenario } from './api/schema';
import { EvidencePanel } from './components/EvidencePanel';
import { ProposalPanel } from './components/ProposalPanel';
import { ThemeToggle } from './components/ThemeToggle';

type Action = 'approve' | 'reject' | 'cancel' | 'repropose' | 'reconcile';
type Attempt = {
  identity: string;
  key: string;
  execute: () => Promise<CaseView>;
};
export default function App() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]),
    [cases, setCases] = useState<CaseView[]>([]);
  const [active, setActive] = useState<CaseView | null>(null),
    [error, setError] = useState('');
  const [pending, setPending] = useState(false),
    [loading, setLoading] = useState(true),
    [selecting, setSelecting] = useState(false),
    [mode, setMode] = useState<'fixture' | 'model'>('fixture');
  const heading = useRef<HTMLHeadingElement>(null),
    busy = useRef(false),
    attempt = useRef<Attempt | null>(null),
    selectionGeneration = useRef(0),
    latest = useRef(new Map<string, CaseView>());
  const remember = useCallback((values: CaseView[]) => {
    const resolved = values.map((value) => {
      const previous = latest.current.get(value.id);
      const next =
        previous && previous.version > value.version ? previous : value;
      latest.current.set(value.id, next);
      return next;
    });
    setCases((inbox) => [
      ...resolved.filter(
        (value) => !inbox.some((item) => item.id === value.id),
      ),
      ...inbox.map((item) => latest.current.get(item.id) ?? item),
    ]);
    return resolved;
  }, []);
  const activeId = active?.id;
  const refresh = useCallback(async () => {
    const inbox = await api.listCases();
    remember(inbox);
  }, [remember]);
  useEffect(() => {
    let alive = true;
    void Promise.all([api.listScenarios(), api.listCases()])
      .then(([samples, inbox]) => {
        if (alive) {
          setScenarios(samples);
          remember(inbox);
        }
      })
      .catch((e: unknown) => {
        if (alive)
          setError(
            e instanceof Error ? e.message : 'Could not load the workbench.',
          );
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [remember]);
  useEffect(() => {
    if (!activeId) return;
    let alive = true;
    let inFlight = false;
    const timer = window.setInterval(() => {
      if (inFlight) return;
      inFlight = true;
      void api
        .getCase(activeId)
        .then((value) => {
          if (alive) {
            const next = remember([value])[0];
            if (next)
              setActive((current) =>
                current?.id === activeId ? next : current,
              );
          }
        })
        .catch((e: unknown) => {
          if (alive)
            setError(e instanceof Error ? e.message : 'Status refresh failed.');
        })
        .finally(() => {
          inFlight = false;
        });
    }, 1000);
    return () => {
      alive = false;
      window.clearInterval(timer);
    };
  }, [activeId, remember]);
  useEffect(() => {
    heading.current?.focus();
  }, [activeId]);
  async function run(
    identity: string,
    factory: (key: string) => () => Promise<CaseView>,
  ) {
    if (busy.current) return;
    busy.current = true;
    selectionGeneration.current += 1;
    setSelecting(false);
    setPending(true);
    setError('');
    if (attempt.current?.identity !== identity) {
      const key = crypto.randomUUID();
      attempt.current = { identity, key, execute: factory(key) };
    }
    try {
      const result = await attempt.current.execute();
      setActive(remember([result])[0] ?? result);
      attempt.current = null;
      await refresh();
    } catch (e: unknown) {
      setError(
        e instanceof Error
          ? e.message
          : 'Request failed. Retry uses the same saved request key.',
      );
    } finally {
      busy.current = false;
      setPending(false);
    }
  }
  function create(scenario: Scenario) {
    void run(
      `create:${scenario.scenario_id}:${mode}`,
      (key) => () =>
        api.createCase(
          {
            scenario_id: scenario.scenario_id,
            order_id: scenario.order_id,
            as_of: scenario.as_of,
            mode,
          },
          key,
        ),
    );
  }
  function act(action: Action) {
    if (!active) return;
    const current = active;
    const identity = `${current.id}:${current.version}:${current.proposal?.hash}:${action}`;
    void run(identity, (key) => {
      if (action === 'approve' || action === 'reject') {
        if (!current.proposal)
          return () => Promise.reject(new Error('No proposal.'));
        const body: ApprovalRequest = {
          proposal_id: current.proposal.id,
          proposal_hash: current.proposal.hash,
          expected_case_version: current.version,
          decision: action,
        };
        return () => api.decide(current.id, body, key);
      }
      return () =>
        api.command(
          current.id,
          action,
          { expected_case_version: current.version },
          key,
        );
    });
  }
  async function select(id: string) {
    if (busy.current) return;
    const generation = ++selectionGeneration.current;
    setSelecting(true);
    try {
      const value = await api.getCase(id);
      if (generation !== selectionGeneration.current) return;
      setActive(remember([value])[0] ?? value);
      if (!attempt.current) setError('');
    } catch (e: unknown) {
      if (generation === selectionGeneration.current)
        setError(e instanceof Error ? e.message : 'Could not open case.');
    } finally {
      if (generation === selectionGeneration.current) setSelecting(false);
    }
  }
  return (
    <>
      <a className="skip-link" href="#case-heading">
        Skip to active case
      </a>
      <header className="site-header">
        <div>
          <div className="eyebrow">BENTO LABS / LOCAL SYSTEMS</div>
          <h1>
            Casework Agent<span className="version">v1</span>
          </h1>
          <p>Delivery exceptions, with evidence before action.</p>
        </div>
        <ThemeToggle />
      </header>
      <div
        className="safety-strip"
        role="region"
        aria-label="Simulation boundary"
      >
        <span className="dot" aria-hidden="true" />
        Fictional records and local services only. Human approval required for
        every write.
      </div>
      {error && (
        <div className="error-banner" role="alert">
          <strong>Action needs attention.</strong> {error}{' '}
          {attempt.current && (
            <button
              disabled={pending}
              onClick={() => {
                const saved = attempt.current;
                if (saved) void run(saved.identity, () => saved.execute);
              }}
            >
              Retry saved request
            </button>
          )}
        </div>
      )}
      <main className="workbench">
        <nav className="inbox" aria-label="Scenarios and cases">
          <div className="section-label">01 / Inbox</div>
          <h2>Case queue</h2>
          <label className="mode-label">
            Decision engine
            <select
              value={mode}
              disabled={pending}
              onChange={(e) => setMode(e.target.value as 'fixture' | 'model')}
            >
              <option value="fixture">Fixture workflow</option>
              <option value="model">Local Qwen model</option>
            </select>
          </label>
          <p className="muted small">
            Fixture mode follows fixed rules. Model mode uses the pinned local
            Qwen snapshot and the shared machine lease.
          </p>
          {scenarios.map((s) => (
            <button
              className="scenario-button"
              key={s.scenario_id}
              disabled={pending}
              onClick={() => create(s)}
            >
              <span>Open {s.title.toLowerCase()}</span>
              <span aria-hidden="true">+</span>
            </button>
          ))}
          <h3 className="queue-label">
            Recent cases <span>{cases.length}</span>
          </h3>
          {loading && <p role="status">Loading cases...</p>}
          {!loading && !cases.length && (
            <p className="muted">
              Your first case starts with the fictional delivery example above.
            </p>
          )}
          <ul className="case-list">
            {cases.map((c) => (
              <li key={c.id}>
                <button
                  aria-current={active?.id === c.id ? 'true' : undefined}
                  disabled={pending}
                  onClick={() => void select(c.id)}
                >
                  <strong>{c.order_id}</strong>
                  <span>{c.state.replaceAll('_', ' ')}</span>
                  <span className="small">
                    {c.mode === 'fixture' ? 'Fixture' : 'Qwen'} /{' '}
                    {c.id.slice(0, 8)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </nav>
        {active ? (
          <div className="active-case">
            <section className="case-header" aria-labelledby="case-heading">
              <div>
                <span className="mode-badge">
                  {active.mode === 'fixture'
                    ? 'Fixture workflow'
                    : 'Actual local model'}
                </span>
                <h2 id="case-heading" tabIndex={-1} ref={heading}>
                  Order {active.order_id}
                </h2>
                <code>{active.id}</code>
              </div>
              <div className="case-status">
                <span className="section-label">Current state</span>
                <strong role="status" aria-live="polite">
                  {active.state.replaceAll('_', ' ')}
                </strong>
                <span>Case version {active.version}</span>
              </div>
              {active.error && (
                <p className="case-error" role="alert">
                  {active.error.message}
                </p>
              )}
            </section>
            {selecting && <p role="status">Loading selected case...</p>}
            <EvidencePanel active={active} />
            <ProposalPanel
              active={active}
              pending={pending || selecting}
              onAction={act}
            />
          </div>
        ) : (
          <section className="empty-state" aria-labelledby="case-heading">
            <div className="section-label">EVIDENCE / APPROVAL / RECOVERY</div>
            <h2 id="case-heading" tabIndex={-1}>
              Every action leaves a trail.
            </h2>
            <p>
              Open a fictional delayed delivery to see the agent gather source
              records, propose an internal action, and wait for your decision.
            </p>
            <div className="empty-steps">
              <span>01 Read source evidence</span>
              <span>02 Review the exact proposal</span>
              <span>03 Confirm both write outcomes</span>
            </div>
          </section>
        )}
      </main>
      <footer>
        LOCAL SIMULATION{' '}
        <span>
          Durable approval. Per-key duplicate protection. Explicit uncertainty.
        </span>
      </footer>
    </>
  );
}
