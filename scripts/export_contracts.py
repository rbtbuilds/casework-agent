import json
from pathlib import Path

from casework_agent.api import create_app
from casework_agent.contracts import CaseView

ROOT = Path(__file__).resolve().parents[1]
(ROOT / 'contracts/openapi.json').write_text(json.dumps(create_app().openapi(), indent=2, sort_keys=True) + '\n')
(ROOT / 'web/src/api/case.schema.json').write_text(json.dumps(CaseView.model_json_schema(mode="serialization"), indent=2, sort_keys=True) + '\n')
