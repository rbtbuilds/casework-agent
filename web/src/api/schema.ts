import Ajv2020 from 'ajv/dist/2020';
import schema from './case.schema.json';
import type { components } from './generated';
export type CaseView = components['schemas']['CaseView'];
export type Operation = components['schemas']['Operation'];
export type ApprovalRequest = components['schemas']['ApprovalRequest'];
export type CaseSeed = components['schemas']['CaseSeed'];
export type VersionRequest = components['schemas']['VersionRequest'];
export type Scenario = { scenario_id: string; order_id: string; as_of: string; title: string };
const validator = new Ajv2020({ strict: false, validateFormats: false }).compile<CaseView>(schema);
export function parseCase(value: unknown): CaseView {
  if (!validator(value)) throw new Error('Server response failed case schema validation.');
  return value;
}
export function parseCases(value: unknown): CaseView[] {
  if (!Array.isArray(value)) throw new Error('Invalid inbox response.');
  return (value as unknown[]).map(parseCase);
}
export function parseScenarios(value: unknown): Scenario[] {
  if (!Array.isArray(value)) throw new Error('Invalid scenario list.');
  return (value as unknown[]).map(item => {
    if (typeof item !== 'object' || item === null || !('scenario_id' in item) || !('order_id' in item) || !('as_of' in item) || !('title' in item) || typeof item.scenario_id !== 'string' || typeof item.order_id !== 'string' || typeof item.as_of !== 'string' || typeof item.title !== 'string') throw new Error('Invalid scenario response.');
    return { scenario_id: item.scenario_id, order_id: item.order_id, as_of: item.as_of, title: item.title };
  });
}
