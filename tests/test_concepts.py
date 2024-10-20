from redactor import redact_concept

def test_redact_concept():
    text = "Enron had a major impact on the energy sector."
    redacted = redact_concept(text, "Enron")
    assert "████ had a major impact on the energy sector." in redacted
