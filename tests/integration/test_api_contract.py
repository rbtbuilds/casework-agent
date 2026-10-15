from pathlib import Path

import pytest

from tests.support import TestSystem


async def test_api_errors_origin_and_full_http_workflow(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.start(app=True)
        bad = await system.api.post('/v1/cases', json={}, headers={'Origin': 'https://unrelated.invalid', 'Idempotency-Key': 'origin'})
        assert bad.status_code == 403 and bad.json()['error']['code'] == 'origin_rejected'
        invalid = await system.api.post('/v1/cases', json={}, headers={'Idempotency-Key': 'invalid'})
        assert invalid.status_code == 422 and invalid.json()['error']['code'] == 'validation_error'
        scenarios = (await system.api.get('/v1/scenarios')).json()
        assert 'expected_action' not in str(scenarios)
        response = await system.api.post('/v1/cases', json={'scenario_id':'dev-delay-01','order_id':'o-001','as_of':'2026-10-15T12:00:00Z','mode':'fixture'}, headers={'Idempotency-Key':'create'})
        assert response.status_code == 201
        case = await system.wait_state(response.json()['id'], 'needs_approval')
        assert case.proposal
        body = {'proposal_id':case.proposal.id,'proposal_hash':case.proposal.hash,'expected_case_version':case.version,'decision':'approve'}
        approved = await system.api.post(f'/v1/cases/{case.id}/decisions', json=body, headers={'Idempotency-Key':'approve'})
        assert approved.status_code == 200
        await system.wait_state(case.id, 'completed')
        replay = await system.api.post(f'/v1/cases/{case.id}/decisions', json=body, headers={'Idempotency-Key':'approve'})
        assert replay.json() == approved.json()
        assert (await system.counts()).tickets == 1
        assert (await system.counts()).annotations == 1


async def test_occupied_port_does_not_stop_owner(tmp_path: Path) -> None:
    async with TestSystem(tmp_path) as system:
        await system.spawn('orders', 'mocks.orders')
        pid = system.processes['orders'].pid
        with pytest.raises(RuntimeError, match='already owned'):
            await system.spawn('orders', 'mocks.orders')
        assert system.processes['orders'].pid == pid
        assert (await system.orders.get('/health')).status_code == 200
