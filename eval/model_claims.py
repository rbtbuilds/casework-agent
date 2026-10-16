from casework_agent.contracts import JsonDict


def summarize_claims(traces: list[JsonDict]) -> JsonDict:
    correct = reasons = complete = fully_correct = evaluated = 0
    for trace in traces:
        diagnostics = trace.get("assessment_diagnostics")
        if not isinstance(diagnostics, dict):
            continue
        fields = diagnostics.get("fields_correct")
        present = diagnostics.get("fields_evaluated")
        if type(fields) is not int or type(present) is not int or not 0 <= fields <= present <= 6:
            continue
        complete += int(present == 6)
        evaluated += present
        correct += fields
        supported = diagnostics.get("reason_supported") is True
        reasons += int(supported)
        fully_correct += int(fields == 6 and supported)
    return {
        "fields_correct": correct,
        "fields_total": 6 * len(traces),
        "fields_incorrect": evaluated - correct,
        "fields_missing": 6 * len(traces) - evaluated,
        "supported_reasons": reasons,
        "reasons_total": len(traces),
        "fully_correct_cases": fully_correct,
        "cases_total": len(traces),
        "complete_assessments": complete,
    }
