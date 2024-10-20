import spacy
from redactor import redact_names

nlp = spacy.load('en_core_web_sm')

def test_redact_names():
    text = "John Doe went to the store."
    doc = nlp(text)
    redacted = redact_names(doc)
    assert "███ ███ went to the store." in redacted
