from redactor import redact_phones
import spacy

nlp = spacy.load('en_core_web_trf')  # Load SpaCy model

def test_redact_phones():
    text = "Call me at 123-456-7890."
    redacted = redact_phones(text)
    assert "Call me at ████████████." in redacted  # 12 blocks expected for the phone number
