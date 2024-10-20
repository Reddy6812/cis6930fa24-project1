import spacy
from redactor import redact_address

nlp = spacy.load('en_core_web_sm')

def test_redact_address():
    text = "I live in New York City."
    doc = nlp(text)
    redacted = redact_address(doc)
    assert "I live in ████████." in redacted
