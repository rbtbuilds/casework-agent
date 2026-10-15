import { parseCase, parseCases, parseScenarios, type ApprovalRequest, type CaseSeed, type VersionRequest } from './schema';
const BASE = 'http://127.0.0.1:8112';
async function request(path: string, body?: object, key?: string): Promise<unknown> {
  const response = await fetch(`${BASE}${path}`, body ? { method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': key ?? '' }, body: JSON.stringify(body) } : {});
  const data: unknown = await response.json();
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    if (typeof data === 'object' && data !== null && 'error' in data && typeof data.error === 'object' && data.error !== null && 'message' in data.error && typeof data.error.message === 'string') message = data.error.message;
    throw new Error(message);
  }
  return data;
}
export const api = {
  listScenarios: async () => parseScenarios(await request('/v1/scenarios')),
  listCases: async () => parseCases(await request('/v1/cases')),
  getCase: async (id: string) => parseCase(await request(`/v1/cases/${encodeURIComponent(id)}`)),
  createCase: async (body: CaseSeed, key: string) => parseCase(await request('/v1/cases', body, key)),
  decide: async (id: string, body: ApprovalRequest, key: string) => parseCase(await request(`/v1/cases/${encodeURIComponent(id)}/decisions`, body, key)),
  command: async (id: string, action: 'cancel' | 'repropose' | 'reconcile', body: VersionRequest, key: string) => parseCase(await request(`/v1/cases/${encodeURIComponent(id)}/${action}`, body, key)),
};
