from .agent import AgentContext, FixtureAdapter, validate_decision
from .config import Settings
from .contracts import ApprovalRequest, CaseView, JsonDict
from .hashing import canonical_hash
from .model_adapter import LocalModelAdapter, ModelClient
from .model_session import ModelSession
from .policy import current_policy
from .repository import Repository
from .tools import ReadTools


class Workflow:
    def __init__(self, repo: Repository, settings: Settings, model: ModelClient | None = None) -> None:
        self.repo, self.settings, self.model = repo, settings, model

    async def gather(self, id: str) -> None:
        if not self.repo.begin_gather(id):
            return
        case = self.repo.get_case(id)
        tools = ReadTools(id, case.order_id, self.settings)
        context = AgentContext(case_id=id, order_id=case.order_id, as_of=case.as_of)
        try:
            if case.mode == "fixture":
                decision = await FixtureAdapter().propose(context, tools)
                trace: JsonDict = {"adapter": "fixture", "usage_tokens": None}
            else:
                if self.model:
                    adapter = LocalModelAdapter(self.model)
                    decision = await adapter.propose(context, tools)
                else:
                    async with ModelSession(self.settings.root) as session:
                        adapter = LocalModelAdapter(session)
                        decision = await adapter.propose(context, tools)
                trace = {"adapter": "model", "usage_tokens": adapter.usage_tokens, "exchange": [m.model_dump(mode="json") for m in adapter.trace]}
            validate_decision(context, tools, decision)
            self.repo.publish(id, decision, tools, trace)
        except (ValueError, RuntimeError, OSError, TimeoutError) as exc:
            self.repo.fail_gather(id, str(exc)[:500])
        finally:
            await tools.close()

    async def decide(self, id: str, request: ApprovalRequest, key: str) -> CaseView:
        fingerprint = canonical_hash(["decision", id, request.model_dump(mode="json")])
        if cached := self.repo.replay(key, fingerprint):
            return cached
        case = self.repo.get_case(id)
        tools = ReadTools(id, case.order_id, self.settings)
        try:
            await tools.get_order(case.order_id)
            assert tools.order
            await tools.get_shipment(tools.order.shipment_id)
            assert tools.shipment
            return self.repo.apply_decision(id, request, key, tools.order.version, tools.shipment.version, canonical_hash(current_policy().model_dump(mode="json")))
        finally:
            await tools.close()
