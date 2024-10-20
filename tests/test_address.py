from redactor import redact_addresses
import spacy

nlp = spacy.load('en_core_web_trf')

def test_redact_address():
    text = "I live in New York City."
    doc = nlp(text)
    redacted = redact_addresses(doc)
    assert "I live in ███ ████ ████ ." in redacted  # Updated expected result
