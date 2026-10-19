"""Bounded, student-authored reflection data; never executes external AI calls."""
from rest_framework import serializers

TEXT_FIELDS = (
    "working_task", "input_data", "expected_result", "required_capabilities",
    "final_justification",
)
CRITERIA = ("quality", "features", "cost", "speed", "privacy", "ease")
PAYLOAD_FIELDS = set(TEXT_FIELDS) | {
    "data_classification", "services", "comparison_criteria", "testing_results", "selected_service",
}


def bounded_text(value, *, maximum=4000, required=False):
    if not isinstance(value, str) or len(value) > maximum:
        raise serializers.ValidationError(f"Enter text up to {maximum} characters.")
    value = value.strip()
    if required and not value:
        raise serializers.ValidationError("This field is required.")
    return value


def validate_map(payload, *, complete):
    if not isinstance(payload, dict):
        raise serializers.ValidationError("Expected an object.")
    if set(payload) - PAYLOAD_FIELDS:
        raise serializers.ValidationError("Unknown selection-map fields.")
    clean, errors = {}, {}
    for field in TEXT_FIELDS:
        if field in payload or complete:
            try:
                clean[field] = bounded_text(payload.get(field, ""), required=complete)
            except serializers.ValidationError as error:
                errors[field] = error.detail
    if "data_classification" in payload or complete:
        classification = payload.get("data_classification")
        if classification not in ("public", "internal", "confidential"):
            errors["data_classification"] = "Choose public, internal or confidential."
        else:
            clean["data_classification"] = classification
    services = payload.get("services", [])
    try:
        if not isinstance(services, list) or len(services) > 3 or (complete and len(services) < 2):
            raise serializers.ValidationError("Compare two or three distinct services.")
        services = [bounded_text(service, maximum=120, required=True) for service in services]
        if len({service.casefold() for service in services}) != len(services):
            raise serializers.ValidationError("Services must be distinct.")
        if "services" in payload or complete:
            clean["services"] = services
    except serializers.ValidationError as error:
        errors["services"] = error.detail
        services = []
    try:
        criteria = payload.get("comparison_criteria", {})
        if not isinstance(criteria, dict) or set(criteria) - set(CRITERIA):
            raise serializers.ValidationError("Use the six provided comparison criteria.")
        if complete and set(criteria) != set(CRITERIA):
            raise serializers.ValidationError("Complete all six comparison criteria.")
        if "comparison_criteria" in payload or complete:
            clean["comparison_criteria"] = {
                key: bounded_text(value, maximum=2000, required=complete)
                for key, value in criteria.items()
            }
    except serializers.ValidationError as error:
        errors["comparison_criteria"] = error.detail
    try:
        results = payload.get("testing_results", [])
        if not isinstance(results, list) or len(results) > 3:
            raise serializers.ValidationError("Provide one result per compared service.")
        normalized = []
        for result in results:
            if not isinstance(result, dict) or set(result) != {"service", "result"}:
                raise serializers.ValidationError("Each result needs service and result text.")
            service = bounded_text(result["service"], maximum=120, required=True)
            if service not in services:
                raise serializers.ValidationError("Results must reference a compared service.")
            normalized.append({"service": service, "result": bounded_text(result["result"], required=complete)})
        names = [item["service"] for item in normalized]
        if len(set(names)) != len(names) or (complete and set(names) != set(services)):
            raise serializers.ValidationError("Provide one result per compared service.")
        if "testing_results" in payload or complete:
            clean["testing_results"] = normalized
    except serializers.ValidationError as error:
        errors["testing_results"] = error.detail
    if "selected_service" in payload or complete:
        selected = payload.get("selected_service", "")
        if not isinstance(selected, str) or len(selected) > 120 or (selected and selected not in services) or (complete and not selected):
            errors["selected_service"] = "Select one of the compared services."
        else:
            clean["selected_service"] = selected
    if errors:
        raise serializers.ValidationError(errors)
    return clean


class SelectionMapWriteSerializer(serializers.Serializer):
    revision = serializers.IntegerField(min_value=0)
    payload = serializers.JSONField()

    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) != {"revision", "payload"}:
            raise serializers.ValidationError({"non_field_errors": ["Provide only revision and payload."]})
        # bool is an int in Python, but is not an optimistic concurrency revision.
        if isinstance(data.get("revision"), bool):
            raise serializers.ValidationError({"revision": "Enter an integer revision."})
        return super().to_internal_value(data)

    def validate_payload(self, value):
        return validate_map(value, complete=self.context.get("complete", False))
