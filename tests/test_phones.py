from redactor import redact_phones

def test_redact_phones():
    text = "Call me at 123-456-7890."
    redacted = redact_phones(text)
    assert "Call me at ██████████." in redacted
