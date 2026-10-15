import type { CaseView } from '../api/schema';
export function EvidencePanel({ active }: { active: CaseView }) {
  return <section className="evidence panel" aria-labelledby="evidence-heading"><div className="section-label">02 / Evidence</div><h2 id="evidence-heading">What the agent read</h2>
    <p className="muted">Source records are untrusted data. They cannot add tools or authorise writes.</p>
    {!active.evidence?.length && <p>Waiting for evidence. No proposal is actionable yet.</p>}
    {active.evidence?.map(e => <article className="evidence-record" key={e.id}><div className="record-heading"><h3>{e.source === 'order' ? 'Order record' : e.source === 'carrier' ? 'Carrier record' : 'Delivery policy'}</h3><span>v{e.source_version.slice(0, 16)}</span></div>
      <dl><dt>Source</dt><dd><code>{e.source_id}</code></dd><dt>Fetched</dt><dd>{new Date(e.fetched_at).toLocaleString()}</dd><dt>Evidence ID</dt><dd><code>{e.id}</code></dd></dl>
      <details><summary>Inspect source and hash</summary><pre>{JSON.stringify(e.payload, null, 2)}</pre><code>{e.payload_hash}</code></details>
    </article>)}
    <h3 className="timeline-heading">Durable timeline</h3><ol className="timeline">{active.events?.map(event => <li key={event.id}><span>{event.kind.replaceAll('_', ' ')}</span><time dateTime={event.created_at}>{new Date(event.created_at).toLocaleTimeString()}</time></li>)}</ol>
  </section>;
}
