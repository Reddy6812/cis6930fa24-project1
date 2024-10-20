from redactor import redact_names
import spacy

nlp = spacy.load('en_core_web_trf')

def test_redact_names():
    text = "John Doe went to the store."
    doc = nlp(text)
    redacted = redact_names(doc)
    assert "████ ███ went to the store ." in redacted  # Adjust for extra space before the period
